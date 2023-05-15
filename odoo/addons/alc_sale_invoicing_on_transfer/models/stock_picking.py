# Copyright 2018 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.partner_invoicing_mode_at_shipping.models.stock_picking import (
    StockPicking as StockPickingBase,
)


class StockPicking(StockPickingBase):
    def _invoice_at_shipping(self):
        return (
            super()._invoice_at_shipping()
            and self.picking_type_id.create_invoice_on_transfer
        )
