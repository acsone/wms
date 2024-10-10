# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.alc_stock_delivery_slip.models.stock_picking import (
    StockPicking as StockPickingBase,
)


class StockPicking(StockPickingBase):
    def _send_delivery_notes(self, send_csv, send_pdf):
        self.ensure_one()
        if any(self.move_ids.rma_id.operation_id.mapped("no_csv_delivery_slip")):
            send_csv = False
        return super()._send_delivery_notes(send_csv, send_pdf)

    def get_entry_register_lines(self):
        if any(
            self.move_ids.rma_receiver_ids.operation_id.mapped(
                "no_entry_register_at_reception"
            )
        ):
            return self.env["stock.move"]
        if any(
            self.move_ids.rma_id.operation_id.mapped("no_entry_register_at_delivery")
        ):
            return self.env["stock.move"]

        return super().get_entry_register_lines()
