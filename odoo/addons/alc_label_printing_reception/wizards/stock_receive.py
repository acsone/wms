# © 2017 Jacques-Etienne Baudoux (BCIM)
# © 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields
from odoo.exceptions import UserError

from odoo.addons.alc_stock_receive_lot.wizards.stock_pack_operation_lot_add import (
    StockPackOperationLotAdd as PackOperationLotAdd,
)


class StockPackOperationLotAdd(PackOperationLotAdd):
    def _default_print_qty(self):
        return 1

    print_qty = fields.Integer(
        "Print Quantity", help="Quantity to print", default=_default_print_qty
    )

    def _add(self):
        res = super()._add()
        self.print_qty = self._default_print_qty()
        return res

    def print_label(self):
        self.ensure_one()
        printer_id = self.env.user.printing_product_label_printer_id.id
        if self.lot_required:
            if not self.lot_name:  # check name because lot is not yet created
                raise UserError(_("Lot is missing"))
            # create a memory record before printing lot label
            lot = self.env["stock.lot"].new(
                {
                    "name": self.lot_name,
                    "product_id": self.product_id.id,
                    "product_qty": self.product_qty,
                    "company_id": self.move_line_id.company_id.id,
                    "expiration_date": self.expiration_date or fields.datetime.now(),
                }
            )
            lot.print_lot_label(self.print_qty, printer_id=printer_id)
        else:
            self.move_line_id.product_id.print_product_label(
                self.print_qty, printer_id=printer_id
            )
