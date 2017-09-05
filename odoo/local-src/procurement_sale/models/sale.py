# -*- coding: utf-8 -*-
# Copyright 2016-2017 Jacques-Etienne Baudoux <je@bcim.be> (BCIM)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields


class SaleOrder(models.Model):
    _inherit = "sale.order"

    confirmation_date = fields.Datetime(
        copy=False,
    )

    @api.multi
    def action_confirm(self):
        # Keep the confirmation date to avoid that Odoo overwrite this date
        confirmation_dates = {}
        for order in self:
            confirmation_dates[order.id] = order.confirmation_date \
                                           or fields.Datetime.now()

        result = super(SaleOrder, self).action_confirm()

        for order in self:
            order.confirmation_date = confirmation_dates[order.id]

        return result


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def _prepare_order_line_procurement(self, group_id):
        vals = super(SaleOrderLine, self)._prepare_order_line_procurement(
            group_id=group_id)
        for line in self.filtered("order_id.confirmation_date"):
            vals.update({
                'date_planned': line.order_id.confirmation_date,
            })
        return vals


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def quants_get_preferred_domain(self, qty, move, ops=False,
                                    lot_id=False, domain=None,
                                    preferred_domain_list=[]):
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
            previous_moves = move.search([
                ('product_id', '=', move.product_id.id),
                ('state', 'in', ['waiting', 'confirmed', 'assigned']),
                ('date', '<', move.date),
                ('location_dest_id', 'in', locations.ids),
                ])
            blocked_qty = sum([x.product_qty for x in previous_moves])
            remaining = move.product_id.qty_available - blocked_qty
            qty = min(qty, max(remaining, 0.0))
            if not qty:
                return self.browse()
        return super(StockQuant, self).quants_get_preferred_domain(
            qty, move, ops=ops, lot_id=lot_id, domain=domain,
            preferred_domain_list=[])
