# -*- coding: utf-8 -*-
# © 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class StockPackOperationLot(models.Model):
    _inherit = 'stock.pack.operation.lot'

    removal_date = fields.Datetime(
        required=True,
        string='Removal date',
    )

    @api.onchange('removal_date')
    def _onchange_removal_date(self):
        if self.removal_date:
            self.lot_name = fields.Date.from_string(
                self.removal_date
            ).strftime('%Y%m%d')

    @api.multi
    def write(self, vals):
        result = super(StockPackOperationLot, self).write(vals)
        if vals.get('lot_id'):
            for pack_operation_lot in self:
                removal_date = pack_operation_lot.removal_date
                if removal_date:
                    pack_operation_lot.lot_id.removal_date = removal_date
                    pack_operation_lot.lot_id.onchange_removal_date()
        return result

    @api.model
    def create(self, vals):
        new_vals = vals.copy()
        if vals.get('lot_id') and not vals.get('removal_date'):
            lot = self.env['stock.production.lot'].browse(vals['lot_id'])
            new_vals['removal_date'] = lot.removal_date
        return super(StockPackOperationLot, self).create(new_vals)
