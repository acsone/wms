# -*- coding: utf-8 -*-
# © 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import date, timedelta

from odoo import fields, models, api, _
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    total_weight = fields.Float('Total weight',
                                compute='_compute_total_weight',
                                readonly=True,
                                help='Total weigh in Kg')

    @api.multi
    def _compute_total_weight(self):
        for po in self:
            total_weight = 0
            for line in po.order_line:
                total_weight += line.product_id.weight * line.product_qty

            po.total_weight = total_weight


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    price_unit_base = fields.Float('Unit Price',
                                   required=True,
                                   digits=dp.get_precision('Product Price'))
    price_unit = fields.Float(string='Unit Price (discounted)',
                              required=False,
                              digits=dp.get_precision('Product Price'),
                              compute='_compute_price_unit',
                              inverse='_set_price_unit',
                              store=True)
    discount_global = fields.Float(
        default=lambda line: line.order_id.partner_id.supplier_discount
    )
    discount_pricelist = fields.Float()
    product_ref = fields.Char('Product ref', related='product_id.default_code')

    @api.multi
    def write(self, vals):
        # The field price_unit is a computed field.
        # If we write the price_unit the method will call the
        # method _set_price_unit which call the method _compute_price_unit.
        # This method will call the method write.
        # At the end we have an infinite loop.
        vals.pop('price_unit', None)
        return super(PurchaseOrderLine, self).write(vals)

    @api.depends('price_unit_base', 'discount_global', 'discount_pricelist')
    def _compute_price_unit(self):
        for line in self:
            price_unit = line.price_unit_base * \
                         (1 - (line.discount_global / 100)) * \
                         (1 - (line.discount_pricelist / 100))
            line.price_unit = price_unit

    def _set_price_unit(self):
        for line in self:
            line.price_unit_base = line.price_unit
        self._compute_price_unit()

    @api.onchange('product_qty', 'product_uom')
    def _onchange_quantity(self):
        result = super(PurchaseOrderLine, self)._onchange_quantity()
        self.price_unit_base = self.price_unit
        self._compute_price_unit()

        return result

    @api.onchange('product_id')
    def onchange_product_id(self):
        result = super(PurchaseOrderLine, self).onchange_product_id()

        date_order = self.order_id.date_order

        date_planned = self.get_next_scheduled_date(date_order)
        self.date_planned = date_planned

        if self.discount_global:
            return result
        self.discount_global = self.order_id.partner_id.supplier_discount

        return result

    @api.model
    def get_next_scheduled_date(self, date_order_str=None):
        """
        Return the scheduled date
        :return: datetime - the scheduled date
        """
        lead_time = \
            int(self.env['ir.config_parameter']
                .get_param('purchase.lead_time', 0))
        if not lead_time:
            raise UserError(_('You need to define the lead time '
                              'on purchase configuration'))

        if date_order_str:
            date_planned = fields.Datetime.from_string(date_order_str)
        else:
            date_planned = date.today()

        holiday_obj = self.env['bank.holiday']
        index = 0
        while index < lead_time:
            date_planned += timedelta(days=1)

            # Check if there is a bank holiday for the current date planned
            date_order_str = fields.Date.to_string(date_planned)
            holiday = holiday_obj.search([('date', '=', date_order_str)])
            if holiday:
                continue

            # Check if the date planned is Saturday or Sunday
            if date_planned.isoweekday() in [6, 7]:
                continue

            index += 1

        return fields.Datetime.to_string(date_planned)

    @api.model
    def _get_date_planned(self, seller, po=False):
        """
        Inherit the method "_get_date_planned" in the module purchase
        The original method has the decorator "api.model" but
        it should be the decorator api.multi or api.one.
        The parameter po is priority on self (see below)
        purchase.py:
        date_order = po.date_order if po else self.order_id.date_order
        :param seller:
        :param po:
        :return:
        """
        date_order_str = po.date_order if po else self.order_id.date_order
        date_planned_str = self.get_next_scheduled_date(date_order_str)

        return fields.Datetime.from_string(date_planned_str)
