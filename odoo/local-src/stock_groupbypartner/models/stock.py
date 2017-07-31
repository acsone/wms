# -*- coding: utf-8 -*-
# Copyright 2016-2017 Jacques-Etienne Baudoux (BCIM)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import UserError


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    groupbypartner = fields.Boolean(
        'Use existing picking having same partner')
    groupbypartner_maxweight = fields.Integer('Max Weight')


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def assign_picking(self):
        """Try to assign the moves to an existing picking
        that has not been reserved yet and that does not have the same
        procurement group but the same partner, locations and picking type
        (moves should already have them identical). Otherwise, create a new
        picking to Assign them to.
        """
        moves_to_group = self.filtered("picking_type_id.groupbypartner")

        moves_to_not_group = self - moves_to_group
        if moves_to_not_group:
            super(StockMove, moves_to_not_group).assign_picking()

        # FIXME TODO: does not work for MTO products.
        pick_obj = self.env["stock.picking"]
        pickings = {}
        pickings_to_recompute = pick_obj.browse()
        for move in moves_to_group:
            domain = [
                ('partner_id', '=', move.group_id.partner_id.id),
                ('location_id', '=', move.location_id.id),
                ('location_dest_id', '=', move.location_dest_id.id),
                ('picking_type_id', '=', move.picking_type_id.id),
                ('printed', '=', False),
                ('state', 'in', ['draft', 'confirmed', 'waiting',
                                 'partially_available', 'assigned'])
            ]
            if str(domain) in pickings:
                picking = pickings[str(domain)]
            else:
                picking = pick_obj.search(domain, limit=1)
                picking = picking and picking[0]
                pickings[str(domain)] = picking

            create = False
            if picking:
                # check weight
                total_weight = 0.0
                if move.picking_type_id.groupbypartner_maxweight:
                    total_weight = move.product_id.weight * move.product_qty
                    for pmove in picking.move_lines:
                        total_weight += (
                            pmove.product_id.weight * pmove.product_qty)
                if (total_weight <=
                        move.picking_type_id.groupbypartner_maxweight):
                    # assign move to picking
                    move.picking_id = picking.id
                    if picking.state in ('confirmed', 'assigned',
                                         'partially_available'):
                        # reserve available qty
                        try:
                            move.action_assign(no_prepare=True)
                        except UserError:
                            # in case of no quant available
                            pass
                        if picking.pack_operation_ids:
                            # recompute pack op
                            pickings_to_recompute |= picking
                else:
                    create = True
            else:
                create = True
            if create:
                values = move._get_new_picking_values()
                picking = pick_obj.create(values)
                pickings[str(domain)] = picking
                move.picking_id = picking.id

        if pickings_to_recompute:
            # recompute pack op
            pickings_to_recompute.do_prepare_partial()
        return True

    @api.multi
    def action_cancel(self):
        """ Prevent to cancel a move from a printed picking and recompute pack
        operations """
        res = super(StockMove, self).action_cancel()
        if self.filtered("picking_id.printed"):
            raise UserError(_("You cannot cancel a move that is part of a started picking"))
        # recompute pack op
        self.mapped('picking_id').do_prepare_partial()
        return res
