# -*- coding: utf-8 -*-
# © 2017 Jacques-Etienne Baudoux (BCIM)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, fields


class StockPackOperationLotAdd(models.TransientModel):
    _inherit = 'stock.pack.operation.lot.add'

    @api.multi
    def print_label(self):
        return self.env.ref(
            'stock_receive_lot.action_pack_operation_lot_add_current').read()[0]
