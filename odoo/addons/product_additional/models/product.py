# -*- coding: utf-8 -*-
# Copyright 2017 Sylvain Van Hoof (Okia SPRL)
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    additional_product_id = fields.Many2one(
        "product.product", string="Additional Product", ondelete="restrict"
    )
    ratio_main_product = fields.Integer("Ratio Main Product")
    ratio_additional_product = fields.Integer("Ratio Additional Product")

    @api.multi
    def get_qty_additional_product(self, ordered_qty):
        self.ensure_one()

        if (
            not self.additional_product_id
            or not self.ratio_main_product
            or not self.ratio_additional_product
        ):
            return 0

        coefficient = self.ratio_main_product / ordered_qty
        qty_additional_product = coefficient * self.ratio_additional_product

        return qty_additional_product

    @api.multi
    def is_an_additional_product(self):
        self.ensure_one()
        return bool(
            len(
                self.env["product.template"].search(
                    [("additional_product_id", "=", self.id)]
                )
            )
        )

    @api.multi
    def get_promotional_product(self, qty, uom):
        """Compute how many promotional product are offered.

        Given a quantity and a unity of measure, returns for the current
        day how many promotional (free) product will be given.
        The unit of measure is adapted if needs be.

        """
        if uom != self.uom_id:
            qty = uom._compute_quantity(qty, self.uom_id)
        result = self.env["product.supplierinfo"].search(
            [
                ("ratio_promotional_product", ">", 0),
                ("ratio_main_product", ">", 0),
                "|",
                ("date_start", "=", False),
                ("date_start", "<=", fields.Date.today()),
                "|",
                ("date_end", "=", False),
                ("date_end", ">=", fields.Date.today()),
                "|",
                ("min_qty_sale", "=", False),
                ("min_qty_sale", "<=", qty),
                ("product_tmpl_id", "=", self.id),
            ],
            order="sequence, min_qty_sale desc, price",
            limit=1,
        )
        if not result:
            return 0
        coefficient = int(qty / result.ratio_main_product)
        return coefficient * result.ratio_promotional_product
