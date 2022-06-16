# -*- coding: utf-8 -*-
# © 2017 Jacques-Etienne Baudoux (BCIM)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models
from odoo.exceptions import UserError


class StockPackOperationLotAdd(models.TransientModel):
    _inherit = "stock.pack.operation.lot.add"

    def _default_print_qty(self):
        return 1

    print_qty = fields.Integer(
        "Print Quantity", help="Quantity to print", default=_default_print_qty
    )

    def _add(self):
        res = super(StockPackOperationLotAdd, self)._add()
        self.print_qty = self._default_print_qty()
        return res

    def print_label(self):
        self.ensure_one()
        printer_id = self.env.user.printing_product_label_printer_id.id
        if self.lot_required:
            if not self.lot_id:
                raise UserError(_("Lot is missing"))
            self.lot_id.print_lot_label(self.print_qty, printer_id=printer_id)
        else:
            self.operation_id.product_id.print_product_label(
                self.print_qty, printer_id=printer_id
            )
