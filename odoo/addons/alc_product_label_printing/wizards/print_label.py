# © 2017 Sylvain Van Hoof (Okia SPRL)
# © 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, fields
from odoo.exceptions import UserError

from odoo.addons.alc_label_printing_base.wizards.print_label import PrintLabel as Label


class PrintLabel(Label):
    label_type = fields.Selection(
        selection_add=[
            ("product", "Product"),
            ("food_product", "Food Product"),
            ("lot", "Lot"),
        ],
        ondelete={"product": "cascade", "food_product": "cascade", "lot": "cascade"},
    )

    def print_label(self):
        self.ensure_one()

        if self.label_type == "product":
            if self.printer_id.type != "toshiba":
                raise UserError(_("Invalid printer"))

            for picking in self.picking_ids:
                picking.print_products_label(
                    printer_id=self.printer_id.id, quantity=self.qty
                )
            return True
        if self.label_type == "food_product":
            if self.printer_id.type != "zebra":
                raise UserError(_("Invalid printer"))
            if self.picking_ids:
                self.print_food_from_picking()

            if self.pack_operation_ids:
                self.print_food_from_packop()
            return True
        return super().print_label()

    def print_food_from_picking(self):
        for picking in self.picking_ids:
            picking.print_food_products_label(
                printer_id=self.printer_id.id, quantity=self.qty
            )
