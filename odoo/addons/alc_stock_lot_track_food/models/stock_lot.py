# Copyright 2023 ACSONE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.stock_lot_track.models.stock_lot import StockLot as StockLotBase


class StockLot(StockLotBase):
    def _calc_name_for_food(self, expiration_date, use_default=False, default=False):
        """The default lot name is only for an aliment."""
        name = default if use_default else self.name
        if self.product_id.is_food:
            name = self._calc_name_from_expiration_date(expiration_date)
        return name

    def _calc_name_from_expiration_date(self, expiration_date):
        date = fields.Datetime.from_string(expiration_date)
        date_with_timezone = fields.Datetime.context_timestamp(self, date)
        return date_with_timezone.strftime("%d%m%y")

    @api.onchange("expiration_date")
    def _onchange_expiration_date(self):
        if self.expiration_date:
            self.name = self._calc_name_for_food(self.expiration_date)
