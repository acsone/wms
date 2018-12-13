# -*- coding: utf-8 -*-
# Copyright 2016-2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api
from odoo.tools.float_utils import float_compare


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def quants_get_preferred_domain(self, qty, move, ops=False,
                                    lot_id=False, domain=None,
                                    preferred_domain_list=[]):
        allowed_qty = qty
        if move.picking_id.picking_type_id.subcode == 'PICK':
            # Do not reserve quantity that is from a previously confirmed SO
            # This allows to reserve quantity in any order. So you can reserve
            # and deliver a customer that has ordered after another one but
            # without using the quantity that is virtually reserved for the
            # first one.
            # You still need to run the procurements in the right order to
            # ensure the delivery orders exist when performing this check.
            locations = self.env['stock.location'].search(
                [('usage', '=', 'customer')])
            previous_moves_domain = [
                ('product_id', '=', move.product_id.id),
                ('state', 'in', ['waiting', 'confirmed', 'assigned']),
                ('date', '<', move.date),
                ('priority', '>=', move.priority),
                ('location_dest_id', 'in', locations.ids),
                ]
            if move.restrict_lot_id:
                previous_moves_domain.append(('restrict_lot_id', '=', move.restrict_lot_id.id))
            previous_moves = move.search(previous_moves_domain)
            blocked_qty = 0
            for pm in previous_moves:
                if pm.location_id.usage in ('view', 'internal'):
                    blocked_qty += pm.product_qty
            # Note that qty_available also consider negative quants. However
            # this is an exception that should not happen
            remaining = move.product_id.qty_available - blocked_qty
            allowed_qty = min(qty, max(remaining, 0.0))
            if not allowed_qty:
                return [(None, qty)]

        res = super(StockQuant, self).quants_get_preferred_domain(
            allowed_qty, move, ops=ops, lot_id=lot_id, domain=domain,
            preferred_domain_list=preferred_domain_list)

        if move.picking_id.picking_type_id.subcode == 'PICK':
            missing_qty = qty - sum([quant[1] for quant in res])
            if float_compare(
                    missing_qty, 0,
                    precision_rounding=move.product_id.uom_id.rounding) > 0:
                for i, reservation in enumerate(res):
                    if reservation[0] is None:
                        res[i] = (None, reservation[1] + missing_qty)
                        break
                else:
                    res.append((None, missing_qty))
        return res
