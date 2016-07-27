# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
from openerp.addons.decimal_precision import decimal_precision as dp


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    promotion_pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string='Supplier Promotion',
        readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
    )

    discount_pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string='Alcyon Discount',
        readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
    )

    @api.model
    def create(self, vals):
        """ Fills promotion and discount pricelist fields (if they are not)
        based on partner configuration.
        """
        pricelists = ('promotion_pricelist_id', 'discount_pricelist_id')
        for pricelist_name in pricelists:
            if pricelist_name not in vals:
                partner_id = vals.get('partner_id')
                if partner_id:
                    partner = self.env['res.partner'].browse(partner_id)
                    pricelist = partner[pricelist_name]
                    if pricelist:
                        vals[pricelist_name] = pricelist.id

        return super(SaleOrder, self).create(vals)

    @api.onchange('partner_id')
    def onchange_partner_id_discount_pricelist(self):
        """ Update promotion and discount pricelist fields
        when partner_id is updated.
        """
        self.promotion_pricelist_id = self.partner_id.promotion_pricelist_id
        self.discount_pricelist_id = self.partner_id.discount_pricelist_id


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    price_unit_supplier = fields.Monetary(
        compute='_compute_amount',
        readonly=True,
        store=True
    )

    price_unit_alcyon = fields.Monetary(
        compute='_compute_amount',
        readonly=True,
        store=True
    )

    supplier_promotion = fields.Float(
        compute='_compute_discount',
        string='Promotion (%)',
        readonly=True,
        digits_compute=dp.get_precision('Discount')
    )
    alcyon_discount = fields.Float(
        compute='_compute_discount',
        string='Discount (%)',
        readonly=True,
        digits_compute=dp.get_precision('Discount')
    )

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """ Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)

            price_supplier = self.apply_discount_pricelist(
                line.product_id, line.order_id.promotion_pricelist_id, price
            )

            if not price_supplier:
                price_alcyon = price_supplier
            else:
                price_alcyon = self.apply_discount_pricelist(
                    line.product_id,
                    line.order_id.discount_pricelist_id,
                    price_supplier
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

    @api.depends('price_unit_supplier', 'price_unit_alcyon')
    def _compute_discount(self):
        """ Compute supplier_promotion and alcyon_discount percentages.
        """
        for line in self:
            if not line.price_unit:
                line.supplier_promotion = 0
                line.alcyon_discount = 0
            else:
                price_unit = line.price_unit
                price_supplier = line.price_unit_supplier
                price_alcyon = line.price_unit_alcyon

                if not price_supplier:
                    line.supplier_promotion = 100
                    line.alcyon_discount = 0

                else:
                    line.supplier_promotion = (
                        (1.0 - price_supplier / price_unit) * 100
                    )

                    line.alcyon_discount = (
                        (1.0 - price_alcyon / price_supplier) * 100
                    )

    @staticmethod
    def apply_discount_pricelist(product, pricelist, price):
        """ Compute a new price by applying *pricelist* on *price*
        """
        if not pricelist:
            return price
        else:
            res = product.with_context(
                override_based_price={product.id: price},
                pricelist=pricelist.id
            )._product_price(None, None)

            return res.get(product.id, 0.0)

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
