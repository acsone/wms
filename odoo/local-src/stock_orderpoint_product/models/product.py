# -*- coding: utf-8 -*-
# © 2016 BCIM sprl (http://www.bcim.be)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    orderpoint_min = fields.Float(
        string='Minimum Quantity',
        compute='_get_orderpoint', inverse='_set_orderpoint')
    orderpoint_max = fields.Float(
        string='Maximum Quantity',
        compute='_get_orderpoint', inverse='_set_orderpoint')
    orderpoint_qty_multiple = fields.Float(
        string='Qty Multiple',
        compute='_get_orderpoint', inverse='_set_orderpoint')
    orderpoint_id = fields.Many2one(
        'stock.warehouse.orderpoint',
        string='Orderpoint',
        readonly=True,
        compute='_get_orderpoint'
    )

    @api.multi
    def _get_orderpoint(self):
        for product in self:
            rules = product.with_context(active_test=False).orderpoint_ids\
                .filtered(lambda r: r.company_id == self.env.user.company_id)
            if rules:
                product.write({
                    'orderpoint_min': rules[0].product_min_qty,
                    'orderpoint_max': rules[0].product_max_qty,
                    'orderpoint_id': rules[0].id,
                    'orderpoint_qty_multiple': rules[0].qty_multiple,
                })

    @api.multi
    def _set_orderpoint(self):
        # The inverse method is not supposed to be used as a setter for
        # multiple fields
        # Here we need to analyse the values of min/max/active fields to
        # decide how to set the orderpoint rule
        # To achieve this, we read directly in cache all the values than
        # can be set
        # We cannot read for self otherwise _get_orderpoint will be called
        # and erase the values
        for product in self:
            rules = product.with_context(
                active_test=False).orderpoint_ids.filtered(
                lambda r: r.company_id == self.env.user.company_id)

            # reading a value that is not set will erase the values that are
            # set as the _get_orderpoint method computes min, max.
            # So we need to retrieve the set values from cache
            omin = product._cache.get('orderpoint_min')
            omax = product._cache.get('orderpoint_max')
            omultiple = product._cache.get('orderpoint_qty_multiple')
            # now get the values that are not set
            if omin is None:
                omin = product.orderpoint_min
            if omax is None:
                omax = product.orderpoint_max
            if omultiple is None:
                omultiple = product.orderpoint_qty_multiple
            # update orderpoint rule
            if rules:
                if omin and omax and omultiple:
                    rules[0].write({
                        'product_min_qty': omin,
                        'product_max_qty': omax,
                        'qty_multiple': omultiple,
                        })
                    # update the cache to ensure next run has the right values
                    # as the inverse method is called
                    # for each field that is set
                    product._cache['orderpoint_min'] = omin
                    product._cache['orderpoint_max'] = omax
                    product._cache['orderpoint_qty_multiple'] = omultiple
                else:
                    rules[0].unlink()
            else:
                if omax and omin and omultiple:
                    rules.create({
                        'product_id': product.id,
                        'product_uom': product.uom_id,
                        'product_min_qty': omin,
                        'product_max_qty': omax,
                        'qty_multiple': omultiple,
                        'active': True,
                        'location_id': self.env.ref(
                            'stock.stock_location_stock').location_id.id,
                        })


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    orderpoint_min = fields.Float(
        string='Minimum Quantity',
        compute='_get_orderpoint', inverse='_set_orderpoint')
    orderpoint_max = fields.Float(
        string='Maximum Quantity',
        compute='_get_orderpoint', inverse='_set_orderpoint')
    orderpoint_qty_multiple = fields.Float(
        string='Qty Multiple',
        compute='_get_orderpoint', inverse='_set_orderpoint')

    @api.multi
    def _get_orderpoint(self):
        for product_tmpl in self:
            if len(product_tmpl.product_variant_ids) > 1:
                return
            product = product_tmpl.product_variant_ids

            rules = product.with_context(active_test=False).orderpoint_ids \
                .filtered(lambda r: r.company_id == self.env.user.company_id)
            if rules:
                product_tmpl.write({
                    'orderpoint_min': rules[0].product_min_qty,
                    'orderpoint_max': rules[0].product_max_qty,
                    'orderpoint_qty_multiple': rules[0].qty_multiple,
                })

    @api.multi
    def _set_orderpoint(self):
        for product_tmpl in self:
            if len(product_tmpl.product_variant_ids) > 1:
                raise UserError(
                    _('You have several variants for this product. '
                      'Please define the min/max on each variant.'))
            product = product_tmpl.product_variant_ids

            # The inverse method is not supposed to be used as a setter for
            # multiple fields
            # Here we need to analyse the values of min/max/active fields to
            # decide how to set the orderpoint rule
            # To achieve this, we read directly in cache all the values that
            # can be set
            # We cannot read for self otherwise _get_orderpoint will be called
            # and erase the values
            rules = product.with_context(active_test=False).orderpoint_ids\
                .filtered(lambda r: r.company_id == self.env.user.company_id)

            # reading a value that is not set will erase the values that are
            # set asthe _get_orderpoint method computes min, max.
            # So we need to retrieve the set values from cache
            omin = product_tmpl._cache.get('orderpoint_min')
            omax = product_tmpl._cache.get('orderpoint_max')
            omultiple = product_tmpl._cache.get('orderpoint_qty_multiple')
            # now get the values that are not set
            if omin is None:
                omin = product_tmpl.orderpoint_min
            if omax is None:
                omax = product_tmpl.orderpoint_max
            if omultiple is None:
                omultiple = product_tmpl.orderpoint_qty_multiple
            # update orderpoint rule
            if rules:
                if omin and omax:
                    rules[0].write({
                        'product_min_qty': omin,
                        'product_max_qty': omax,
                        'qty_multiple': omultiple,
                    })
                    # update the cache to ensure next run has the right values
                    # as the inverse method is called
                    # for each field that is set
                    product_tmpl._cache['orderpoint_min'] = omin
                    product_tmpl._cache['orderpoint_max'] = omax
                    product_tmpl._cache['orderpoint_qty_multiple'] = omultiple
                else:
                    rules[0].unlink()
            elif omax and omin and omultiple:
                rules.create({
                    'product_id': product.id,
                    'product_uom': product.uom_id,
                    'product_min_qty': omin,
                    'product_max_qty': omax,
                    'qty_multiple': omultiple,
                    'active': True,
                    'location_id': self.env.ref(
                        'stock.stock_location_stock').location_id.id,
                })
