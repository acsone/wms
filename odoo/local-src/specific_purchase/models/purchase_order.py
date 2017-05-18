# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA, Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models, api
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

    @api.model
    def create(self, vals):
        """
        All purchase order are automatically confirmed
        """
        po = super(PurchaseOrder, self).create(vals)
        po.button_confirm()

        return po


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
    supplier_product_ref = fields.Char('Supplier ref',
                                       compute='_compute_supplier_product_ref',
                                       readonly=True)

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

        if self.discount_global:
            return result
        self.discount_global = self.order_id.partner_id.supplier_discount

        return result

    @api.multi
    def _compute_supplier_product_ref(self):
        for line in self:
            seller = line.product_id._select_seller(
                partner_id=line.partner_id,
                quantity=line.product_qty,
                date=line.order_id.date_order
                     and line.order_id.date_order[:10],
                uom_id=line.product_uom)

            if seller:
                line.supplier_product_ref = seller.product_code
