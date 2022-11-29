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
        zone_equipment = self.env.ref("__setup__.picking_zone_materiel")
        zone_cold = self.env.ref("__setup__.picking_zone_frigo")
        zone_food = self.env.ref("__setup__.picking_zone_aliments")
        zone_med = self.env.ref("__setup__.picking_zone_humain")
        zones = (zone_med, zone_cold, zone_food, zone_equipment)
        # Check quantities for packages
        for picking in self:
            nbr_of_packages_by_zone = defaultdict(set)
            item_number_of_drug = 0
            item_number_of_cold = 0
            item_number_of_food = 0
            item_number_of_equipment = 0
            item_number_total = 0
            item_numbers = (
                item_number_of_drug,
                item_number_of_cold,
                item_number_of_food,
                item_number_of_equipment,
                item_number_total,
            )
            for operation in picking.pack_operation_ids:
                if operation.package_id and operation.package_id.is_internal:
                    for op in operation.package_id.planned_pack_operation_ids:
                        item_numbers = self._compute_number_of_items(
                            picking, op, item_numbers, zones
                        )
                elif operation.package_id and not operation.package_id.is_internal:
                    if not operation.package_id.original_picking_zone_id:
                        raise UserError(
                            _("There is no original picking zone on " "this operation.")
                        )
                    picking_zone = operation.package_id.original_picking_zone_id
                    if operation.package_id:
                        nbr_of_packages_by_zone[picking_zone].add(
                            operation.package_id.id
                        )
                else:
                    item_numbers = self._compute_number_of_items(
                        picking, operation, item_numbers, zones
                    )
            picking.number_of_equipment = sum(
                self.env["stock.quant.package"]
                .browse(nbr_of_packages_by_zone[zone_equipment])
                .mapped("nbr_packages")
            )
            picking.number_of_cold = sum(
                self.env["stock.quant.package"]
                .browse(nbr_of_packages_by_zone[zone_cold])
                .mapped("nbr_packages")
            )
            picking.number_of_food = sum(
                self.env["stock.quant.package"]
                .browse(nbr_of_packages_by_zone[zone_food])
                .mapped("nbr_packages")
            )
            picking.number_of_drug = sum(
                self.env["stock.quant.package"]
                .browse(nbr_of_packages_by_zone[zone_med])
                .mapped("nbr_packages")
            )
            picking.number_total = (
                picking.number_of_equipment
                + picking.number_of_cold
                + picking.number_of_food
                + picking.number_of_drug
            )

            picking.item_number_of_drug = item_numbers[0]
            picking.item_number_of_cold = item_numbers[1]
            picking.item_number_of_food = item_numbers[2]
            picking.item_number_of_equipment = item_numbers[3]
            picking.item_number_total = item_numbers[4]

    def _compute_number_of_items(self, picking, operation, item_numbers, zones):
        """
        item_numbers = (item_number_of_drug, item_number_of_cold, item_number_of_food, item_number_of_equipment, item_number_total)
        zones = (zone_med, zone_cold, zone_food, zone_equipment)
        """
        if not operation.product_id.categ_id:
            raise UserError(_("There is no category on this product"))

        picking_zone = operation.product_id.picking_zone_id
        qty = operation.qty_done

        item_number_of_drug = item_numbers[0]
        item_number_of_cold = item_numbers[1]
        item_number_of_food = item_numbers[2]
        item_number_of_equipment = item_numbers[3]
        item_number_total = item_numbers[4]

        item_number_total += qty

        if picking_zone == zones[0]:
            item_number_of_drug += qty
        elif picking_zone == zones[1]:
            item_number_of_cold += qty
        elif picking_zone == zones[2]:
            item_number_of_food += qty
        elif picking_zone == zones[3]:
            item_number_of_equipment += qty
        else:
            self.env.user.notify_error(
                _(
                    "Picking zone does not exist anymore %s for picking %s and product %s"
                )
                % (
                    picking_zone.name,
                    picking.name,
                    operation.product_id.product_tmpl_id.name,
                )
            )
        item_numbers = (
            item_number_of_drug,
            item_number_of_cold,
            item_number_of_food,
            item_number_of_equipment,
            item_number_total,
        )
        return item_numbers
