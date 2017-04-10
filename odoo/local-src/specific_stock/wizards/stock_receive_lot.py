# -*- coding: utf-8 -*-
# © 2017 Jacques-Etienne Baudoux (BCIM)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields


class StockPackOperationLotAdd(models.TransientModel):
    _inherit = 'stock.pack.operation.lot.add'

    qty_backorder = fields.Integer(
        'Backorder',
        compute='_get_qty_backorder')

    @api.depends('operation_id')
    @api.one
    def _get_qty_backorder(self):
        # TODO: Maybe improve with real qty in BO.
        # Note that self.operation_id.qty_backorder is the amount of BO lines,
        # not the total qty in BO
        self.qty_backorder = self.operation_id.qty_backorder and True or False
