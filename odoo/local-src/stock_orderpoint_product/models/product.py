# -*- coding: utf-8 -*-
# © 2016 BCIM sprl (http://www.bcim.be)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    orderpoint_min = fields.Float('Minimum Quantity')
    orderpoint_max = fields.Float('Maximum Quantity')
    orderpoint_qty_multiple = fields.Float('Qty Multiple')

    @api.constrains('orderpoint_min', 'orderpoint_max',
                    'orderpoint_qty_multiple')
    def constrains_orderpoint(self):
        """
        Set orderpoint values from products to the model orderpoint
        :return:
        """
        # Use only for songs
        if self.env.context.get('disable_constrains_orderpoint'):
            return

        for product_tmpl in self:
            product = product_tmpl.product_variant_ids[0]

            rules = product.orderpoint_ids \
                .filtered(lambda r: r.company_id == self.env.user.company_id)
            if rules:
                rules.write({
                    'product_min_qty': product.orderpoint_min,
                    'product_max_qty': product.orderpoint_max,
                    'qty_multiple': product.orderpoint_qty_multiple,
                })
            else:
                product.orderpoint_ids.create({
                    'product_id': product.id,
                    'product_uom': product.uom_id,
                    'product_min_qty': product.orderpoint_min,
                    'product_max_qty': product.orderpoint_max,
                    'qty_multiple': product.orderpoint_qty_multiple,
                    'active': True,
                    'location_id': self.env.ref(
                        'stock.stock_location_stock').location_id.id,
                })
