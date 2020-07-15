# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Sylvain Van Hoof <svh@sylvainvh.be>
#    Copyright 2016 BCIM sprl, Camptocamp
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from collections import defaultdict

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    price_total = fields.Monetary(
        string="Total", compute="_compute_price_total", readonly=True
    )
    currency_id = fields.Many2one(
        "res.currency", string="Currency", compute="_compute_price_total"
    )

    number_of_drug = fields.Float(
        "Number of medical", compute="_compute_number_of_products"
    )
    number_of_cold = fields.Float(
        "Number of cold", compute="_compute_number_of_products"
    )
    number_of_food = fields.Float(
        "Number of food", compute="_compute_number_of_products"
    )
    number_of_human_drug = fields.Float(
        "Number of human drug", compute="_compute_number_of_products"
    )
    number_of_equipment = fields.Float(
        "Number of equipments", compute="_compute_number_of_products"
    )
    number_total = fields.Float(
        "Number of boxes", compute="_compute_number_of_products"
    )

    item_number_of_drug = fields.Float(
        "Number of medical products", compute="_compute_number_of_products"
    )
    item_number_of_cold = fields.Float(
        "Number of cold products", compute="_compute_number_of_products"
    )
    item_number_of_food = fields.Float(
        "Number of food products", compute="_compute_number_of_products"
    )
    item_number_of_human_drug = fields.Float(
        "Number of human drug products", compute="_compute_number_of_products"
    )
    item_number_of_equipment = fields.Float(
        "Number of equipments products", compute="_compute_number_of_products"
    )
    item_number_total = fields.Float(
        "Number of products", compute="_compute_number_of_products"
    )

    def _compute_price_total(self):
        for picking in self:
            lines_done = picking.move_lines.filtered(lambda line: line.state == "done")

            currency = lines_done.mapped("order_id.currency_id")
            if not currency:
                currency = picking.company_id.currency_id

            if len(currency) != 1:
                raise UserError(_("There are more than one currencies on orders"))

            picking.price_total = sum(
                line.order_line_id.price_reduce_taxinc * line.product_qty
                for line in lines_done
            )
            picking.currency_id = currency.id

    @api.depends("move_lines", "move_lines.product_id", "move_lines.product_uom_qty")
    def _compute_number_of_products(self):
        zone_drug = self.env.ref("__setup__.picking_zone_medicament")
        zone_equipment = self.env.ref("__setup__.picking_zone_materiel")
        zone_cold = self.env.ref("__setup__.picking_zone_frigo")
        zone_food = self.env.ref("__setup__.picking_zone_aliments")
        zone_human = self.env.ref("__setup__.picking_zone_humain")

        # Check quantities for packages
        for picking in self:
            nbr_of_packages_by_zone = defaultdict(set)

            for operation in picking.pack_operation_pack_ids:
                if not operation.package_id.original_picking_zone_id:
                    raise UserError(
                        _("There is no original picking zone on " "this operation.")
                    )

                picking_zone = operation.package_id.original_picking_zone_id

                if operation.package_id:
                    nbr_of_packages_by_zone[picking_zone].add(operation.package_id.id)

            picking.number_of_drug = sum(
                [
                    x
                    for x in self.env["stock.quant.package"]
                    .browse(nbr_of_packages_by_zone[zone_drug])
                    .mapped("nbr_packages")
                ]
            )
            picking.number_of_equipment = sum(
                [
                    x
                    for x in self.env["stock.quant.package"]
                    .browse(nbr_of_packages_by_zone[zone_equipment])
                    .mapped("nbr_packages")
                ]
            )
            picking.number_of_cold = sum(
                [
                    x
                    for x in self.env["stock.quant.package"]
                    .browse(nbr_of_packages_by_zone[zone_cold])
                    .mapped("nbr_packages")
                ]
            )
            picking.number_of_food = sum(
                [
                    x
                    for x in self.env["stock.quant.package"]
                    .browse(nbr_of_packages_by_zone[zone_food])
                    .mapped("nbr_packages")
                ]
            )
            picking.number_of_human_drug = sum(
                [
                    x
                    for x in self.env["stock.quant.package"]
                    .browse(nbr_of_packages_by_zone[zone_human])
                    .mapped("nbr_packages")
                ]
            )
            picking.number_total = (
                picking.number_of_drug
                + picking.number_of_equipment
                + picking.number_of_cold
                + picking.number_of_food
                + picking.number_of_human_drug
            )

            item_number_of_drug = 0
            item_number_of_cold = 0
            item_number_of_food = 0
            item_number_of_human_drug = 0
            item_number_of_equipment = 0
            item_number_total = 0

            # Check quantities for products without pack
            for operation in picking.pack_operation_product_ids:
                if not operation.product_id.categ_id:
                    raise UserError(_("There is no category on this product"))

                picking_zone = operation.product_id.picking_zone_id

                qty = operation.qty_done
                item_number_total += qty

                if picking_zone == zone_drug:
                    item_number_of_drug += qty
                elif picking_zone == zone_cold:
                    item_number_of_cold += qty
                elif picking_zone == zone_food:
                    item_number_of_food += qty
                elif picking_zone == zone_equipment:
                    item_number_of_equipment += qty
                elif picking_zone == zone_human:
                    item_number_of_human_drug += qty
                else:
                    raise UserError(
                        _("The picking zone %s is not correct") % picking_zone.name
                    )

            picking.item_number_of_drug = item_number_of_drug
            picking.item_number_of_cold = item_number_of_cold
            picking.item_number_of_food = item_number_of_food
            picking.item_number_of_human_drug = item_number_of_human_drug
            picking.item_number_of_equipment = item_number_of_equipment
            picking.item_number_total = item_number_total
