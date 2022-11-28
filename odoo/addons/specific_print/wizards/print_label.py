# -*- coding: utf-8 -*-
# © 2017 Sylvain Van Hoof (Okia SPRL)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PrintLabel(models.TransientModel):
    _name = "print.label"

    label_type = fields.Selection(
        [
            ("product", "Product"),
            ("package", "Package"),
            ("lot", "Lot"),
            ("food_product", "Food Product"),
        ],
        string="Label type",
        required=True,
    )
    printer_id = fields.Many2one("printing.printer", string="Printer", required=True)
    picking_ids = fields.Many2many("stock.picking", string="Pickings")
    lot_ids = fields.Many2many("stock.production.lot", string="Lots")
    pack_operation_ids = fields.Many2many(
        "stock.pack.operation", string="Pack operations"
    )
    qty = fields.Integer("Quantity", default=1)

    @api.model
    def default_get(self, fields_list=None):
        if not fields_list:
            fields_list = {}

        result = super(PrintLabel, self).default_get(fields_list)

        active_model = self._context.get("active_model")
        active_ids = self._context.get("active_ids", [])
        if active_model == "stock.picking":
            result["picking_ids"] = [(6, 0, active_ids)]
        elif active_model == "stock.production.lot":
            result["lot_ids"] = [(6, 0, active_ids)]
        elif active_model == "stock.pack.operation":
            result["pack_operation_ids"] = [(6, 0, active_ids)]
        else:
            raise UserError(_("Invalid model"))

        return result

    @api.multi
    def print_label(self):
        self.ensure_one()

        if self.label_type == "product":
            if self.printer_id.type != "toshiba":
                raise UserError(_("Invalid printer"))

            for picking in self.picking_ids:
                picking.print_products_label(
                    printer_id=self.printer_id.id, quantity=self.qty
                )
        elif self.label_type == "package":
            if self.printer_id.type != "zebra":
                raise UserError(_("Invalid printer"))

            for picking in self.picking_ids:
                picking.print_packages_label(
                    printer_id=self.printer_id.id, quantity=self.qty
                )

        elif self.label_type == "lot":
            if self.printer_id.type != "zebra":
                raise UserError(_("Invalid printer"))

            for lot in self.lot_ids:
                lot.print_lot_label(printer_id=self.printer_id.id, quantity=self.qty)

        elif self.label_type == "food_product":
            if self.printer_id.type != "zebra":
                raise UserError(_("Invalid printer"))
            if self.picking_ids:
                self.print_food_from_picking()

            if self.pack_operation_ids:
                self.print_food_from_packop()

    def print_food_from_picking(self):
        for picking in self.picking_ids:
            picking.print_food_products_label(
                printer_id=self.printer_id.id, quantity=self.qty
            )

    def print_food_from_packop(self):
        for packop in self.pack_operation_ids:
            do_not_print_food_labels = packop.partner_id.no_labels_food_products
            if packop.pack_lot_ids:
                for pack_lot in packop.pack_lot_ids:
                    packop.print_food_product_label(
                        printer_id=self.printer_id.id,
                        quantity=self.qty,
                        lot_id=pack_lot.lot_id,
                        do_not_print_food_labels=do_not_print_food_labels,
                    )
            else:
                packop.print_food_product_label(
                    printer_id=self.printer_id.id,
                    quantity=self.qty,
                    do_not_print_food_labels=do_not_print_food_labels,
                )
