# -*- coding: utf-8 -*-
# © 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import datetime, timedelta

from openerp import models, fields, api


class StockPackOperationLot(models.Model):
    _inherit = 'stock.pack.operation.lot'

    life_date = fields.Datetime(
        string='End of Life Date')
    is_removal_date_expired = fields.Boolean(
        'Removal date', readonly=True)

    def _calc_is_expired(self, product, life_date):
        is_removal_date_expired = False

        if life_date:
            if product.removal_time:
                date = fields.Datetime.from_string(life_date)
                removal_time = product.removal_time
                removal_date = date - timedelta(days=removal_time)
                if removal_date < datetime.now():
                    is_removal_date_expired = True
        return is_removal_date_expired

    def _calc_lotname_from_lifedate(self, life_date):
        date = fields.Datetime.from_string(life_date)
        date_with_timezone = fields.Datetime.context_timestamp(self, date)
        return date_with_timezone.strftime('%Y%m%d')

    @api.onchange('life_date')
    def _onchange_life_date(self):
        if self.life_date:
            self.lot_name = self._calc_lotname_from_lifedate(self.life_date)

        self.is_removal_date_expired = self._calc_is_expired(
            self.operation_id.product_id, self.life_date)

    @api.multi
    def write(self, vals):
        result = super(StockPackOperationLot, self).write(vals)
        if vals.get('lot_id'):
            for pack_operation_lot in self:
                life_date = pack_operation_lot.life_date
                if life_date:
                    pack_operation_lot.lot_id.life_date = life_date
                    pack_operation_lot.lot_id.onchange_life_date()
        return result

    @api.model
    def create(self, vals):
        if vals.get('lot_id') and not vals.get('life_date'):
            lot = self.env['stock.production.lot'].browse(vals['lot_id'])
            vals['life_date'] = lot.life_date
        return super(StockPackOperationLot, self).create(vals)
