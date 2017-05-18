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

        if self.discount_global:
            return result
        self.discount_global = self.order_id.partner_id.supplier_discount

        return result
