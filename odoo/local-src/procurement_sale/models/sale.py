# -*- coding: utf-8 -*-
# Copyright 2016-2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _
from odoo.exceptions import UserError
from odoo.tools import float_compare


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
    def write(self, values):
        """ If the route has changed, we need to adapt the procurement. Cancel
        it and recreate it """
        changed_lines = False
        if 'route_id' in values:
            changed_lines = self.filtered(lambda r: r.state == 'sale')
            if changed_lines:
                changed_lines.mapped('procurement_ids').cancel()
                if 'product_uom_qty' in values:
                    # then procurement is already recreated in standard
                    precision = self.env['decimal.precision'].precision_get(
                        'Product Unit of Measure')
                    changed_lines -= self.filtered(
                        lambda r: r.state == 'sale' and float_compare(
                            r.product_uom_qty, values['product_uom_qty'],
                            precision_digits=precision) == -1)
        result = super(SaleOrderLine, self).write(values)
        if changed_lines:
            changed_lines._action_procurement_create()
        return result

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
