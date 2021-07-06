# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    theoritical_number_of_packages = fields.Integer(
        "Theoritical number of packages in a picking out",
        compute="_compute_theoritical_number_of_packages",
    )
    number_of_packages_done = fields.Integer(
        "Number of packages in a picking out", compute="_compute_number_of_packages",
    )
    is_number_of_packages_visible = fields.Boolean(
        "Number of packages visible",
        compute="_compute_is_number_of_packages_visible",
        default=False,
    )
    is_number_of_packages_outranged = fields.Boolean(
        "Too many packages compared to the theoritical number",
        compute="_compute_is_number_of_packages_outranged",
        default=False,
    )

    @api.depends(
        "picking_type_code", "carrier_id", "carrier_id.maximum_weight_per_package"
    )
    def _compute_is_number_of_packages_visible(self):

        for rec in self:
            if (
                rec.picking_type_code == "outgoing"
                and rec.carrier_id.maximum_weight_per_package
            ):
                rec.is_number_of_packages_visible = True
            else:
                rec.is_number_of_packages_visible = False

    @api.depends("is_number_of_packages_visible", "move_lines")
    def _compute_theoritical_number_of_packages(self):
        for rec in self:
            if rec.is_number_of_packages_visible:
                products_weights = rec.move_lines.mapped("product_id.weight")
                number_of_items = rec.move_lines.mapped("product_uom_qty")
                rec.theoritical_number_of_packages = rec._number_of_packages(
                    products_weights,
                    number_of_items,
                    rec.carrier_id.maximum_weight_per_package,
                )

    @api.depends(
        "is_number_of_packages_visible",
        "pack_operation_ids",
        "pack_operation_ids.result_package_id",
    )
    def _compute_number_of_packages(self):
        for rec in self:
            if rec.is_number_of_packages_visible:
                rec.number_of_packages_done = len(
                    rec.mapped("pack_operation_ids.result_package_id")
                )

    @api.depends("theoritical_number_of_packages", "number_of_packages")
    def _compute_is_number_of_packages_outranged(self):
        for rec in self:
            rec.is_number_of_packages_outranged = (
                rec.number_of_packages_done > rec.theoritical_number_of_packages
            )

    def _number_of_packages(
        self, products_weights, number_of_items, maximum_weight_per_package
    ):

        # Split the product_weights into as many items as we haves
        products_weights_list = []
        for weight, number in zip(products_weights, number_of_items):
            for i in range(int(number)):
                products_weights_list.append(weight)

        products_weights_list.sort()

        i = 0
        weight = 0
        j = len(products_weights_list) - 1
        theoritical_number_of_packages = 0
        while i <= j:
            theoritical_number_of_packages += 1
            # Try to fit the heaviest product with the lightest.
            # If it does not work, then the heaviest should have
            # a box to himself
            weight = products_weights_list[i] + products_weights_list[j]
            while weight <= maximum_weight_per_package:
                i += 1
                if i < j:
                    # While the weight of products does not exceed the limit,
                    # continue adding products in the same package
                    weight += products_weights_list[i]
                else:
                    break

            j -= 1

        return theoritical_number_of_packages
