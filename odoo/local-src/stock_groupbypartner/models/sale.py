# -*- coding: utf-8 -*-
# Copyright 2016-2017 Jacques-Etienne Baudoux (BCIM)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    @api.depends('procurement_group_id')
    def _compute_picking_ids(self):
        for order in self:
            order.picking_ids = self.env['stock.move'].search([
                ('group_id', '=', order.procurement_group_id.id)
                ]).mapped('picking_id') if order.procurement_group_id else []
            order.delivery_count = len(order.picking_ids)

    @api.multi
    def action_confirm(self):
        """ Do not group pickings having a dedicated carrier """
        self_carrier = self.filtered('carrier_id')
        if self_carrier:
            super(SaleOrder, self_carrier.with_context(
                nogrouppicking=True)).action_confirm()
        self_nocarrier = self - self_carrier
        if self_nocarrier:
            super(SaleOrder, self_nocarrier).action_confirm()
