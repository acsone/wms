# © 2017 Sylvain Van Hoof (Okia SPRL)
# © 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, fields
from odoo.exceptions import UserError

from odoo.addons.alc_label_printing_base.wizards.print_label import PrintLabel as Label
from odoo.addons.stock.models.stock_lot import StockLot
from odoo.addons.stock.models.stock_move_line import StockMoveLine


class PrintLabel(Label):
    label_type = fields.Selection(
        selection_add=[
            ("product", "Product"),
            ("food_product", "Food Product"),
            ("lot", "Lot"),
        ],
        ondelete={"product": "cascade", "food_product": "cascade", "lot": "cascade"},
    )
    lot_ids = fields.Many2many[StockLot](string="Lots")
    move_line_ids = fields.Many2many[StockMoveLine](string="Pack operations")

    def default_get(self, fields_list=None):
        result = super().default_get(fields_list)
        active_model = self.env.context.get("active_model")
        active_ids = self.env.context.get("active_ids", [])
        if active_model == self.picking_ids._name:
            result["picking_ids"] = [fields.Command.set(active_ids)]
        elif active_model == self.lot_ids._name:
            result["lot_ids"] = [fields.Command.set(active_ids)]
        return result

    def print_label(self):  # noqa: C901
        self.ensure_one()

        if self.label_type == "product":
            if self.printer_id.type != "toshiba":
                raise UserError(_("Invalid printer (-> toshiba)"))

            for picking in self.picking_ids:
                picking.print_products_label(
                    printer_id=self.printer_id.id, quantity=self.qty
                )
            return True
        if self.label_type == "food_product":
            if self.printer_id.type != "zebra":
                raise UserError(_("Invalid printer (-> zebra)"))
            if self.picking_ids:
                self.print_food_from_picking()

            if self.move_line_ids:
                self.print_food_from_move_lines()
            return True
        if self.label_type == "lot":
            if self.printer_id.type != "zebra":
                raise UserError(_("Invalid printer"))

            for lot in self.lot_ids:
                lot.print_lot_label(printer_id=self.printer_id.id, quantity=self.qty)
            return True
        return super().print_label()

    def print_food_from_picking(self):
        for picking in self.picking_ids:
            picking.print_food_products_label(
                printer_id=self.printer_id.id, quantity=self.qty
            )

    def print_food_from_move_lines(self):
        for move_line in self.move_line_ids:
            do_not_print_food_labels = (
                move_line.picking_id.partner_id.no_labels_food_products
            )
            if move_line.lot_id:
                move_line.print_food_product_label(
                    printer_id=self.printer_id.id,
                    quantity=self.qty,
                    quantity_done=move_line.qty_done,
                    lot_id=move_line.lot_id,
                    do_not_print_food_labels=do_not_print_food_labels,
                )
            else:
                move_line.print_food_product_label(
                    printer_id=self.printer_id.id,
                    quantity=self.qty,
                    quantity_done=move_line.qty_done,
                    do_not_print_food_labels=do_not_print_food_labels,
                )
