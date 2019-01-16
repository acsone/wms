# -*- coding: utf-8 -*-
# Copyright 2016 Vincent Renaville (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models, api


class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    @api.multi
    def _create_returns(self):
        picking = self.env['stock.picking'].browse(
            self.env.context['active_id'])
        # we want to do unpack only for customer return
        if picking.location_dest_id.usage == 'customer':
            quant_obj = self.env['stock.quant']
            return_moves = self.product_return_moves.mapped('move_id')
            for move in return_moves:
                # search associate quants
                quants = quant_obj.search([
                    ('history_ids', 'in', move.id),
                    ('package_id', '!=', False),
                    ('location_id', 'child_of', move.location_dest_id.id)
                ])
                for quant in quants:
                    quant.package_id.unpack()
        return super(ReturnPicking, self)._create_returns()
