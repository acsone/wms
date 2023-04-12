# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.alc_stock_receive_lot.wizards import stock_pack_operation_lot_add


class StockPackOperationLotAdd(stock_pack_operation_lot_add.StockPackOperationLotAdd):

    is_removal_date_expired = fields.Boolean(
        "Removal Date Expired", compute="_compute_is_removal_date_expired"
    )

    @api.depends("expiration_date", "move_line_id")
    def _compute_is_removal_date_expired(self):
        for wizard in self:
            if not wizard.move_line_id:
                wizard.is_removal_date_expired = False
            else:
                lot = self.env["stock.lot"].new(
                    {
                        "product_id": wizard.move_line_id.product_id.id,
                        "expiration_date": wizard.expiration_date,
                    }
                )
                wizard.is_removal_date_expired = lot.product_expiry_alert
