# Copyright 2023 ACSONE SA/NV

from odoo.addons.alce_stock_barcode_easy_operation.models import stock_picking


class StockPicking(stock_picking.StockPicking):
    def _get_std_view_action(self, res_id=None):
        action_picking_form = self.env.ref("stock_barcode.stock_picking_action_form")
        action_picking_form = action_picking_form.read()[0]
        action_picking_form["res_id"] = res_id or self.id
        return {"action": action_picking_form}

    def on_barcode_scanned(self, barcode):
        # Avoid bad code popup after the button barcode has been treated
        if barcode.startswith("O-BTN."):
            return None
        return super().on_barcode_scanned(barcode)
