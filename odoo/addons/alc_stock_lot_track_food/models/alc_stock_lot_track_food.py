# Copyright 2023 ACSONE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.stock_lot_track.models.stock_lot import StockLot as StockLotBase


class StockLot(StockLotBase):
    def _calc_lotname_for_food(self, expiration_date):
        """The default lot name is only for an aliment."""
        lot_name = self.lot_name
        if self.product_id.is_food:
            self._calc_lotname_from_expiration_date(expiration_date)
        return lot_name

    def _calc_lotname_from_expiration_date(self, expiration_date):
        date = fields.Datetime.from_string(expiration_date)
        date_with_timezone = fields.Datetime.context_timestamp(self, date)
        return date_with_timezone.strftime("%d%m%y")

    @api.onchange("expiration_date")
    def _onchange_expiration_date(self):
        if self.expiration_date:
            self.lot_name = self._calc_lotname_for_food(self.expiration_date)
