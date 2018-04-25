# -*- coding: utf-8 -*-
# Copyright 2016-2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _
from odoo.exceptions import UserError


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
            if order.confirmation_date:
                confirmation_dates[order.id] = order.confirmation_date

        result = super(SaleOrder, self).action_confirm()

        for order in self:
            if order.id in confirmation_dates:
                order.confirmation_date = confirmation_dates[order.id]

        return result


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def _prepare_order_line_procurement(self, group_id):
        vals = super(SaleOrderLine, self)._prepare_order_line_procurement(
            group_id=group_id)
        if not self.order_id.confirmation_date:
            raise UserError(_(
                'Missing sale order confirmation date. '
                'Cannot plan delivery procurement order'))
        vals['date_planned'] = self.order_id.confirmation_date
        if self.route_id.priority:
            vals['priority'] = self.route_id.priority
        return vals
