# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.addons.decimal_precision import decimal_precision as dp

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

    @api.model
    def get_values_for_additional_line(
            self,
            new_product,
            new_quantity,
            additional_product,
            position,
            line
    ):
        values = super(Sale, self).get_values_for_additional_line(
            new_product,
            new_quantity,
            additional_product,
            position,
            line
        )
        line_model = self.env['sale.order.line']
        qty_unavailable = line_model.get_product_qty_unavailable(
            new_product,
            values['product_uom_qty']
        )
        values['product_qty_unavailable'] = qty_unavailable

        return values

    @api.model
    def get_current_values_for_additional_line(self, current_line, line):
        current_values = super(
            Sale, self
        ).get_current_values_for_additional_line(current_line, line)
        qty_unavailable = current_line.product_qty_unavailable
        current_values['product_qty_unavailable'] = qty_unavailable
        return current_values


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

    product_qty_unavailable = fields.Float(
        string='Quantity unavailable',
        digits=dp.get_precision('Product Unit of Measure'),
        readonly=True,
    )

    current_product_qty_unavailable = fields.Float(
        string='Current quantity unavailable',
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_compute_current_product_qty_unavailable',
    )

    def _compute_current_product_qty_unavailable(self):
        for line in self:
            line.current_product_qty_unavailable = 5

    difference_qty_unavailable = fields.Float(
        string='Difference quantity unavailable',
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_compute_difference_qty_unavailable',
    )

    def _compute_difference_qty_unavailable(self):
        for line in self:
            line.difference_qty_unavailable = 10

    @api.onchange('product_uom_qty')
    def onchange_for_product_qty_unavailable(self):
        context = self.env.context or {}
        if context.get('must_compute_product_qty_unavailable'):
            for line in self:
                line.product_qty_unavailable = \
                    self.get_product_qty_unavailable(
                        self.product_id,
                        self.product_uom_qty
                    )

    @api.model
    def get_product_qty_unavailable(self, product, product_uom_qty):
        if product and product_uom_qty:
            qty_available = product.qty_available
            return (
                qty_available - product_uom_qty
            )
        else:
            return None

    @api.multi
    def onchange(self, values, field_name, field_onchange):
        new_context = self.env.context.copy() if self.env.context else {}
        if isinstance(field_name, list):
            if 'product_uom_qty' in field_name:
                new_context['must_compute_product_qty_unavailable'] = True
        else:
            if field_name == 'product_uom_qty':
                new_context['must_compute_product_qty_unavailable'] = True
        return super(SaleOrderLine, self.with_context(new_context)).onchange(
            values, field_name, field_onchange
        )

    @api.model
    def create(self, vals):
        record = super(SaleOrderLine, self).create(vals)
        if vals.get('product_uom_qty'):
            # Because product_qty_unavailable is readonly,
            # we need to apply the onchange
            # on create to save the correct values.
            #
            # Without that,
            # the product_qty_unavailable isn't sent by form view,
            # and its value isn't save.
            record.with_context(
                must_compute_product_qty_unavailable=True
            ).onchange_for_product_qty_unavailable()
        return record

    @api.multi
    def write(self, vals):
        result = super(SaleOrderLine, self).write(vals)
        if vals.get('product_uom_qty'):
            # Because product_qty_unavailable is readonly,
            # we need to apply the onchange
            # on write to save the correct values.
            #
            # Without that,
            # the product_qty_unavailable isn't sent by form view,
            # and its value isn't save.
            self.with_context(
                must_compute_product_qty_unavailable=True
            ).onchange_for_product_qty_unavailable()
        return result


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
