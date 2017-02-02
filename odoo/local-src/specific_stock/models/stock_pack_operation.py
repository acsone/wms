# -*- coding: utf-8 -*-
# © 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import datetime, timedelta

from openerp import models, fields, api


class StockPackOperationLot(models.Model):
    _inherit = 'stock.pack.operation.lot'

    life_date = fields.Datetime(
        string='End of Life Date',
    )
    is_removal_date_expired = fields.Boolean('Removal date', default=False)

    @api.onchange('life_date')
    def _onchange_life_date(self):
        if self.life_date:
            date = fields.Datetime.from_string(self.life_date)
            date_with_timezone = fields.Datetime.context_timestamp(self, date)
            self.lot_name = date_with_timezone.strftime('%Y%m%d')

            if self.operation_id.product_id.categ_id.removal_time:
                removal_time = \
                    self.operation_id.product_id.categ_id.removal_time
                removal_date = \
                    date - timedelta(days=removal_time)
                if removal_date < datetime.now():
                    self.is_removal_date_expired = True
                else:
                    self.is_removal_date_expired = False

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
        new_vals = vals.copy()
        if vals.get('lot_id') and not vals.get('life_date'):
            lot = self.env['stock.production.lot'].browse(vals['lot_id'])
            new_vals['life_date'] = lot.life_date
        return super(StockPackOperationLot, self).create(new_vals)
