# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _prepare_procurement_from_move(self):
        res = super(StockMove, self)._prepare_procurement_from_move()
        res['restrict_lot_id'] = self.restrict_lot_id.id
        return res

    def _assign_picking_group_domain(self):
        domain = super(StockMove, self)._assign_picking_group_domain()
        picking_ids = self.move_orig_ids.mapped('picking_id')
        if picking_ids and not picking_ids.mapped('delivery_round_id'):
            domain += [
                '|',
                ('delivery_round_id', '=', False),
                ('delivery_round_id.state', '=', 'draft'),
            ]
        return domain
