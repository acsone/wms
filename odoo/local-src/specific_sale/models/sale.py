# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class Sale(models.Model):
    _inherit = 'sale.order'

    sale_channel = fields.Selection([
        ('phone', 'Phone'),
        ('mail', 'Mail'),
        ('fax', 'Fax'),
    ])

    sale_channel_visible = fields.Boolean(
        compute='_compute_sale_channel_required'
    )

    @api.depends('team_id')
    def _compute_sale_channel_required(self):
        direct_team = self.env.ref('sales_team.team_sales_department')
        for record in self:
            if direct_team and record.team_id == direct_team:
                record.sale_channel_visible = True
            else:
                record.sale_channel_visible = False

    @api.onchange('team_id')
    def onchange_team_id(self):
        if self.sale_channel_visible and not self.sale_channel:
            self.sale_channel = 'phone'
        elif not self.sale_channel_visible:
            self.sale_channel = False


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    exception = fields.Char(
        compute='_compute_exception',
    )

    @api.depends('product_id', 'price_unit', 'price_subtotal')
    def _compute_exception(self):
        line_exceptions = self.env['sale.exception'].search(
            [('model', '=', 'sale.order.line')],
            order='id'
        )

        for line in self:
            exception = ''
            if line.product_id:
                for rule in line_exceptions:
                    if self.env['sale.order']._rule_eval(rule, 'line', line):
                        exception = rule.description
                        break
            line.exception = exception


# Override the inherit of sale_product_additional
# to complete sale.order.line.original with new specific fields
class SaleOrderLineOriginal(models.Model):
    _name = 'sale.order.line.original'
    _inherit = 'sale.order.line'


# Override the inherit of sale_product_additional
# to complete sale.order.line.additional with new specific fields
class SaleOrderLineAdditional(models.Model):
    _name = 'sale.order.line.additional'
    _inherit = 'sale.order.line'
