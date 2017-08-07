# -*- coding: utf-8 -*-
# © 2016-2017 Jacques-Etienne Baudoux (BCIM)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, _
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def action_assign(self, no_prepare=False):
        """ Picking's moves must be assigned to a delivery round to be reserved
        """
        if not self.env.context.get('round_autoset', True):
            return super(StockMove, self).action_assign(
                no_prepare=no_prepare)

        pick_moves = self.filtered(
            lambda m: m.picking_id.picking_type_subcode == 'PICK')
        has_assigned = False
        for picking in pick_moves.mapped('picking_id'):
            _logger.debug(
                "Searching a delivery round for picking %s to assign" %
                picking.id)
            if not picking.delivery_round_id:
                delivery_round = self.env['round.instance'].find(
                    picking.partner_id)
                if delivery_round:
                    delivery_round._assign_pickings(picking)
                    has_assigned = True
        other_moves = self - pick_moves
        if other_moves:
            super(StockMove, other_moves).action_assign(
                no_prepare=no_prepare)
            has_assigned = True
        if pick_moves and not has_assigned:
            pass
            # Thread not happy with this warning:
            # raise UserError(_("No delivery round instance found"))

    @api.multi
    @api.constrains('picking_id')
    def _check_round(self):
        if not self.mapped('picking_id.delivery_round_id'):
            return
        for move in self:
            # when a picking is assigned to a move, we have to ensure the whole
            # group (all dest moves) has the same delivery round
            orig_drs = move.mapped('move_orig_ids').mapped(
                'picking_id.delivery_round_id')
            if len(orig_drs) > 1:
                raise ValidationError(_(
                    "All pickings at destination of a same shipping must "
                    "be in the same delivery round"))
