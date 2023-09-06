# Copyright 2016 BCIM sprl, Camptocamp
# Copyright 2023 ACSONE SA/NV

from collections import defaultdict

from odoo import _, api, fields
from odoo.exceptions import UserError

from odoo.addons.stock.models.stock_picking import Picking
from odoo.addons.base.models.res_currency import Currency


class StockPicking(Picking):

    price_total = fields.Monetary(
        string="Total", compute="_compute_price_total", readonly=True
    )
    currency_id = fields.Many2one[Currency](
        string="Currency", compute="_compute_price_total"
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

    def _compute_number_of_items(self, picking, move_line, item_numbers, pick_types):
        """
        Item_numbers = (item_number_of_drug, item_number_of_cold, item_number_of_food,.

                        item_number_of_equipment, item_number_total)
        pick_types = (pick_type_med, pick_type_cold, pick_type_food,
                      pick_type_equipment)
        """
        if not move_line.product_id.categ_id:
            raise UserError(_("There is no category on this product"))

        pick_type = move_line.picking_type_id
        qty = move_line.qty_done

        item_number_of_drug = item_numbers[0]
        item_number_of_cold = item_numbers[1]

        item_number_of_food = item_numbers[2]
        item_number_of_equipment = item_numbers[3]
        item_number_total = item_numbers[4]

        item_number_total += qty

        if pick_type == pick_types[0]:
            item_number_of_drug += qty
        elif pick_type == pick_types[1]:
            item_number_of_cold += qty
        elif pick_type == pick_types[2]:
            item_number_of_food += qty
        elif pick_type == pick_types[3]:
            item_number_of_equipment += qty
        elif pick_type == pick_types[4]:
            pass
        else:
            self.env.user.notify_danger(
                _(
                    "Picking type does not exist anymore %(pictypename)s for picking "
                    "%(pickname)s and product %(prodname)s",
                    pictypename=pick_type.name,
                    pickname=picking.name,
                    prodname=move_line.product_id.product_tmpl_id.name,
                ),
                sticky=False,
            )
        item_numbers = (
            item_number_of_drug,
            item_number_of_cold,
            item_number_of_food,
            item_number_of_equipment,
            item_number_total,
        )
        return item_numbers

    @api.depends("move_ids", "move_ids.product_id", "move_ids.product_uom_qty")
    def _compute_number_of_products(self):
        pick_type_equipment = self.env.ref("__setup__.stock_picking_type_materiel")
        pick_type_cold = self.env.ref("__setup__.stock_picking_type_froid")
        pick_type_food = self.env.ref(
            "alc_stock_picking_type_aliment.stock_picking_type_ali"
        )
        pick_type_med = self.env.ref("__custom__.stock_picking_type_medoc")
        pick_type_out = self.env.ref("stock.picking_type_out")
        pick_types = (
            pick_type_med,
            pick_type_cold,
            pick_type_food,
            pick_type_equipment,
            pick_type_out,
        )
        # Check quantities for packages
        for picking in self:
            nbr_of_packages_by_pick_type = defaultdict(set)
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
            for move_line in picking.move_line_ids:
                if move_line.package_id and move_line.package_id.is_internal:
                    for ml in move_line.package_id.planned_move_line_ids:
                        item_numbers = self._compute_number_of_items(
                            picking, ml, item_numbers, pick_types
                        )
                else:
                    item_numbers = self._compute_number_of_items(
                        picking, move_line, item_numbers, pick_types
                    )
            picking.number_of_equipment = sum(
                self.env["stock.quant.package"]
                .browse(nbr_of_packages_by_pick_type[pick_type_equipment])
                .mapped("number_of_parcels")
            )
            picking.number_of_cold = sum(
                self.env["stock.quant.package"]
                .browse(nbr_of_packages_by_pick_type[pick_type_cold])
                .mapped("number_of_parcels")
            )
            picking.number_of_food = sum(
                self.env["stock.quant.package"]
                .browse(nbr_of_packages_by_pick_type[pick_type_food])
                .mapped("number_of_parcels")
            )
            picking.number_of_drug = sum(
                self.env["stock.quant.package"]
                .browse(nbr_of_packages_by_pick_type[pick_type_med])
                .mapped("number_of_parcels")
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
