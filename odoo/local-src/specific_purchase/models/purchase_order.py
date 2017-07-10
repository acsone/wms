# -*- coding: utf-8 -*-
# © 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import date, timedelta

from odoo import fields, models, api
import odoo.addons.decimal_precision as dp


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    total_weight = fields.Float('Total weight',
                                compute='_compute_total_weight',
                                readonly=True,
                                help='Total weigh in Kg')
    responsible_id = fields.Many2one('res.users',
                                     string='Responsible',
                                     track_visibility='onchange')

    @api.multi
    def _compute_total_weight(self):
        for po in self:
            total_weight = 0
            for line in po.order_line:
                total_weight += line.product_id.weight * line.product_qty

            po.total_weight = total_weight

    @api.multi
    def button_confirm(self):
        self.responsible_id = self.env.user.id

        return super(PurchaseOrder, self).button_confirm()

    last_date_done = fields.Datetime(
        string='Last date of Transfer',
        compute='_compute_last_date_done',
        store=True,
    )

    @api.depends('order_line.qty_received')
    def _compute_last_date_done(self):
        for order in self:
            if order.is_shipped:
                order.last_date_done = max(
                    order.picking_ids.mapped('date_done')
                )
            else:
                order.last_date_done = False


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    price_unit_base = fields.Float('Unit Price',
                                   required=True,
                                   digits=dp.get_precision('Product Price'))
    price_unit = fields.Float(string='Unit Price (discounted)')
    discount_global = fields.Float(
        default=lambda line: line.order_id.partner_id.supplier_discount
    )
    discount_pricelist = fields.Float()
    product_ref = fields.Char('Product ref', related='product_id.default_code')

    # By default there is no way to add a discounts in Purchase Lines.
    # To do that I added a new field "price_unit_base".
    # This field will replace the field "price_unit" in the view form and the
    # field price_unit will contains the price of the product with discount.
    #
    # When the user create a Purchase Order Line he will set the price
    # on price_unit_base and recompute the price with discount.
    @api.model
    def create(self, vals):
        """
        To keep a good compatibility we set the price_unit_base if
        the user create a purchase_order_line without price_unit_base
        (and vice versa)
        :param vals:
        :return:
        """
        if 'price_unit' in vals and 'price_unit_base' not in vals:
            vals['price_unit_base'] = vals['price_unit']

        if 'price_unit_base' in vals and 'price_unit' not in vals:
            vals['price_unit'] = vals['price_unit_base']

        return super(PurchaseOrderLine, self).create(vals)

    @api.multi
    def write(self, vals):
        """
        To keep a good compatibility we set the price_unit_base if the user
        change the price_unit we need to recompute the price_unit_base.

        To avoid infinite loop we need to not write the price_unit_base
        when we recompute the price_unit.
        """
        if 'price_unit' in vals \
                and 'price_unit_base' not in vals\
                and not self.env.context.get('stop_constrains'):
            vals['price_unit_base'] = vals['price_unit']

        return super(PurchaseOrderLine, self).write(vals)

    @api.constrains('price_unit_base', 'discount_global', 'discount_pricelist')
    @api.onchange('price_unit_base', 'discount_global', 'discount_pricelist')
    def _compute_price_unit(self):
        """
        This method will compute the price unit according
        the price_unit_base with discounts.

        I use the api constrains and the onchange to ensure that
        the price unit will be compute in any case.
        The API onchange will be use in the form view to directly compute
        the the unit_price and display the right price on the view.
        The API constrains will be use if a method change a discount
        or the price_unit (see above the method write).
        """
        for line in self:
            price_unit = line.price_unit_base * \
                         (1 - (line.discount_global / 100)) * \
                         (1 - (line.discount_pricelist / 100))
            line.with_context(stop_constrains=True).price_unit = price_unit

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

        if self.product_id:
            order_date_str \
                = self.order_id.date_order and self.order_id.date_order[:10]
            seller = self.product_id._select_seller(
                partner_id=self.partner_id,
                quantity=self.product_qty,
                date=order_date_str,
                uom_id=self.product_uom)
            date_planned = self.get_next_scheduled_date(seller, date_order)
            self.date_planned = date_planned

        if self.discount_global:
            return result
        self.discount_global = self.order_id.partner_id.supplier_discount

        return result

    @api.model
    def get_next_scheduled_date(self, seller, date_order_str=None):
        """
        Return the scheduled date
        :return: datetime - the scheduled date
        """

        if seller:
            lead_time = seller.delay
        else:
            lead_time = \
                int(self.env['ir.config_parameter']
                    .get_param('purchase.lead_time', 0))

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
        date_planned_str = self.get_next_scheduled_date(seller, date_order_str)

        return fields.Datetime.from_string(date_planned_str)
