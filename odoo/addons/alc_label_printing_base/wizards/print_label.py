# © 2017 Sylvain Van Hoof (Okia SPRL)
# © 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, fields, models
from odoo.exceptions import UserError

from odoo.addons.alc_printing_base.models.printing_printer import PrintingPrinter
from odoo.addons.stock.models.stock_lot import StockLot
from odoo.addons.stock.models.stock_move_line import StockMoveLine
from odoo.addons.stock.models.stock_picking import Picking


class PrintLabel(models.TransientModel):
    _name = "print.label"
    _description = "Print label wizard"

    label_type = fields.Selection(
        selection=[("package", "Package")],
        string="Label type",
        required=True,
    )
    printer_id = fields.Many2one[PrintingPrinter](string="Printer", required=True)
    picking_ids = fields.Many2many[Picking](string="Pickings")
    lot_ids = fields.Many2many[StockLot](string="Lots")
    pack_operation_ids = fields.Many2many[StockMoveLine](string="Pack operations")
    qty = fields.Integer("Quantity", default=1)

    def default_get(self, fields_list=None):
        if not fields_list:
            fields_list = {}

        result = super().default_get(fields_list)

        active_model = self._context.get("active_model")
        active_ids = self._context.get("active_ids", [])
        if active_model == "stock.picking":
            result["picking_ids"] = [fields.Command.set(active_ids)]
        elif active_model == "stock.production.lot":
            result["lot_ids"] = [fields.Command.set(active_ids)]
        elif active_model == "stock.move.operation":
            result["pack_operation_ids"] = [fields.Command.set(active_ids)]
        else:
            raise UserError(_("Invalid model"))

        return result

    def print_label(self):
        self.ensure_one()

        if self.label_type == "package":
            if self.printer_id.type != "zebra":
                raise UserError(_("Invalid printer"))
            for picking in self.picking_ids:
                picking.print_packages_label(
                    printer_id=self.printer_id.id, quantity=self.qty
                )
