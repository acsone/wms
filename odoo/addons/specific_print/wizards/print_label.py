# -*- coding: utf-8 -*-
# © 2017 Sylvain Van Hoof (Okia SPRL)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PrintLabel(models.TransientModel):
    _name = "print.label"

    label_type = fields.Selection(
        [("product", "Product"), ("package", "Package"), ("lot", "Lot")],
        string="Label type",
        required=True,
    )
    printer_id = fields.Many2one("printing.printer", string="Printer", required=True)
    picking_ids = fields.Many2many("stock.picking", string="Pickings")
    lot_ids = fields.Many2many("stock.production.lot", string="Lots")
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
