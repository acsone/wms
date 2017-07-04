# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    supplier_promotion_allowed = fields.Boolean(
        string='Supplier promotion allowed',
        states={
            'draft': [('readonly', False)],
            'sent': [('readonly', False)]
        },
    )

    discount_pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string='Alcyon Discount',
        readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
    )

    @api.model
    def create(self, vals):
        """ Fills discount pricelist field (if it is not)
        based on partner configuration.
        """
        if 'discount_pricelist_id' not in vals:
            partner_id = vals.get('partner_id')
            if partner_id:
                partner = self.env['res.partner'].browse(partner_id)
                pricelist = partner['discount_pricelist_id']
                if pricelist:
                    vals['discount_pricelist_id'] = pricelist.id

        return super(SaleOrder, self).create(vals)

    @api.onchange('partner_id')
    def onchange_partner_id_discount_pricelist(self):
        """ Update promotion and discount pricelist fields
        when partner_id is updated.
        """
        self.supplier_promotion_allowed = (
            self.partner_id.supplier_promotion_sale_allowed
        )
        self.discount_pricelist_id = self.partner_id.discount_pricelist_id


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    price_unit_supplier = fields.Monetary(
        compute='_compute_amount',
        store=True,
        readonly=True,
    )

    price_unit_alcyon = fields.Monetary(
        compute='_compute_amount',
        store=True,
        readonly=True,
    )

    supplier_promotion = fields.Float(
        compute='_compute_discount',
        string='Promotion (%)',
        digits=dp.get_precision('Discount'),
    )
    alcyon_discount = fields.Float(
        compute='_compute_discount',
        string='Discount (%)',
        digits=dp.get_precision('Discount'),
    )

    edited_supplier_promotion = fields.Float(
        digits=dp.get_precision('Discount'),
    )

    edited_alcyon_discount = fields.Float(
        digits=dp.get_precision('Discount'),
    )

    @api.depends(
        'product_uom_qty', 'discount', 'price_unit', 'tax_id',
        'edited_supplier_promotion', 'edited_alcyon_discount',
        'order_id.supplier_promotion_allowed',
        'order_id.discount_pricelist_id'
    )
    def _compute_amount(self):
        """ Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)

            if line.edited_supplier_promotion or line.edited_alcyon_discount:
                price_supplier, price_alcyon = line._compute_discount_prices(
                    price
                )
            else:
                price_supplier, price_alcyon = line._compute_pricelist_prices(
                    price
                )

            taxes = line.tax_id.compute_all(
                price_alcyon, line.order_id.currency_id,
                line.product_uom_qty,
                product=line.product_id, partner=line.order_id.partner_id
            )
            line.update({
                'price_unit_supplier': price_supplier,
                'price_unit_alcyon': price_alcyon,
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    def _compute_pricelist_prices(self, price):
        """ Compute supplier_unit_price and alcyon_unit_price based on
        price_unit and sale.order pricelists.
        """
        self.ensure_one()

        price_supplier = price
        condition = (
            self.product_id and
            self.order_id.supplier_promotion_allowed
        )
        if condition:

            seller = self.product_id._select_seller_for_sale(
                partner_id=False,
                quantity=self.product_uom_qty,
                date=(
                    self.order_id.date_order and self.order_id.date_order[:10]
                ),
                uom_id=self.product_uom
            )

            if seller:
                price_supplier = price * (1 - seller.discount_sale / 100)

        if not price_supplier:
            price_alcyon = price_supplier
        else:
            price_alcyon = self.apply_discount_pricelist(
                self.product_id,
                self.order_id.discount_pricelist_id,
                price_supplier
            )
        return price_supplier, price_alcyon

    def _compute_discount_prices(self, price):
        """ Compute supplier_unit_price and alcyon_unit_price based on
        price_unit and supplier_promotion / alcyon_discount.
        """

        self.ensure_one()

        currency_round = self.order_id.currency_id.round

        price_supplier = currency_round(
            price * (1 - (self.edited_supplier_promotion or 0) / 100.0)
        )

        if not price_supplier:
            price_alcyon = price_supplier
        else:
            price_alcyon = currency_round(
                price_supplier * (
                    1 - (self.edited_alcyon_discount or 0) / 100.0
                )
            )

        return price_supplier, price_alcyon

    @api.depends('price_unit_supplier', 'price_unit_alcyon')
    def _compute_discount(self):
        """ Compute supplier_promotion and alcyon_discount percentages.
        """
        for line in self:
            if line.edited_supplier_promotion or line.edited_alcyon_discount:
                line.update({
                    'supplier_promotion': line.edited_supplier_promotion,
                    'alcyon_discount': line.edited_alcyon_discount,
                })

            else:
                if not line.price_unit:
                    line.update({
                        'supplier_promotion': 0,
                        'alcyon_discount': 0,
                    })
                else:
                    price_unit = line.price_unit
                    price_supplier = line.price_unit_supplier
                    price_alcyon = line.price_unit_alcyon

                    if not price_supplier:
                        line.update({
                            'supplier_promotion': 100,
                            'alcyon_discount': 0,
                        })

                    else:
                        line.update({
                            'supplier_promotion': (
                                (1.0 - price_supplier / price_unit) * 100
                            ),
                            'alcyon_discount': (
                                (1.0 - price_alcyon / price_supplier) * 100
                            ),
                        })

    @api.multi
    def onchange(self, values, field_name, field_onchange):
        new_context = self.env.context.copy() if self.env.context else {}
        if isinstance(field_name, list):
            condition = (
                'supplier_promotion' in field_name or
                'alcyon_discount' in field_name
            )
            if condition:
                new_context['apply_onchange_promotion_discount'] = True
        else:
            if field_name in ['supplier_promotion', 'alcyon_discount']:
                new_context['apply_onchange_promotion_discount'] = True
        return super(SaleOrderLine, self.with_context(new_context)).onchange(
            values, field_name, field_onchange
        )

    @api.onchange('supplier_promotion', 'alcyon_discount')
    def onchange_promotion_discount(self):
        """ Force inverse call on discount to fill manual discounts.
        """
        if self.env.context.get('apply_onchange_promotion_discount'):
            self.update({
                'edited_supplier_promotion': self.supplier_promotion,
                'edited_alcyon_discount': self.alcyon_discount,
            })

    @api.onchange('product_id')
    def onchange_product_id_reset_discount(self):
        """ If product of order line is changed, we reset the manual discount.
        """
        self.update({
            'edited_supplier_promotion': False,
            'edited_alcyon_discount': False
        })

    @staticmethod
    def apply_discount_pricelist(product, pricelist, price):
        """ Compute a new price by applying *pricelist* on *price*
        """
        if not pricelist:
            return price
        else:
            product_temporary = product.with_context(
                override_based_price={product.id: price},
                pricelist=pricelist.id
            ).browse(product.id)
            return product_temporary.price

    @api.multi
    def _prepare_invoice_line(self, qty):
        """ Calls parent method and adds supplier and alcyon discounts
        in result dict.
        """
        self.ensure_one()
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)

        res.update({
            'supplier_promotion': self.supplier_promotion,
            'alcyon_discount': self.alcyon_discount,
        })

        return res
