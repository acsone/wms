# -*- coding: utf-8 -*-
# © 2016 BCIM sprl (http://www.bcim.be)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    orderpoint_min = fields.Float('Minimum Quantity')
    orderpoint_max = fields.Float('Maximum Quantity')
    orderpoint_qty_multiple = fields.Float('Qty Multiple')

    _orderpoint_fields = (
        'orderpoint_min',
        'orderpoint_max',
        'orderpoint_qty_multiple',
    )

    def _propagate_orderpoint(self):
        """
        Set orderpoint values from products to the model orderpoint
        :return:
        """
        # Use only for songs
        if self.env.context.get('disable_constrains_orderpoint'):
            return

        for product_tmpl in self:
            # In some case (see the method create on product.product)
            # the product_template may not have a variant.
            # In this case, we have to skip this constrains
            product_variant = product_tmpl.with_context(
                active_test=False
            ).product_variant_ids

            if not product_variant:
                continue
            product = product_variant[0]

            rules = product.orderpoint_ids.filtered(
                lambda r: r.company_id == self.env.user.company_id
            )
            if rules:
                rules.write(
                    {
                        'product_min_qty': product.orderpoint_min,
                        'product_max_qty': product.orderpoint_max,
                        'qty_multiple': product.orderpoint_qty_multiple,
                        'active': product.active,
                    }
                )
            else:
                product.orderpoint_ids.create(
                    {
                        'product_id': product.id,
                        'product_uom': product.uom_id,
                        'product_min_qty': product.orderpoint_min,
                        'product_max_qty': product.orderpoint_max,
                        'qty_multiple': product.orderpoint_qty_multiple,
                        'location_id': self.env.ref(
                            'stock.stock_location_stock'
                        ).location_id.id,
                        'active': product.active,
                    }
                )

    @api.model
    def create(self, vals):
        record = super(ProductTemplate, self).create(vals)
        if any(field in vals for field in self._orderpoint_fields):
            record._propagate_orderpoint()
        return record

    @api.multi
    def write(self, values):
        """If a product has been changed to a type service
        you can archive the orderpoints with context.

        Used only for import.
        """
        if (
            self._context.get('force_archive_orderpoint')
            and 'type' in values
            and values['type'] != 'product'
            and sum(self.mapped('nbr_reordering_rules')) != 0
        ):
            ops = self.mapped('product_variant_ids.orderpoint_ids').filtered(
                lambda r: r.active
            )
            ops.write({'active': False})
            # recompute value of `nbr_reordering_rules`
            self.invalidate_cache(['nbr_reordering_rules'])

        result = super(ProductTemplate, self).write(values)

        if any(field in values for field in self._orderpoint_fields):
            self._propagate_orderpoint()
        return result


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def create(self, vals):
        """
        When a product.product is created, Odoo will create the product
        and only after that create the product.template. At the end, Odoo
        will write the link between the product and the template.
        :param vals:
        :return:
        """
        orderpoint_min = vals.pop('orderpoint_min', 0)
        orderpoint_max = vals.pop('orderpoint_max', 0)
        orderpoint_qty_multiple = vals.pop('orderpoint_qty_multiple', 0)

        result = super(ProductProduct, self).create(vals)

        if orderpoint_min or orderpoint_max or orderpoint_qty_multiple:
            result.product_tmpl_id.write(
                {
                    'orderpoint_min': orderpoint_min,
                    'orderpoint_max': orderpoint_max,
                    'orderpoint_qty_multiple': orderpoint_qty_multiple,
                }
            )

        return result

    def write(self, values):
        """If a product is archived you can propagate
        archiving to orderpoints with context.

        Used only for import.
        """
        if (
            self._context.get('force_archive_orderpoint')
            and 'active' in values
            and not values['active']
        ):
            ops = self.mapped('orderpoint_ids').filtered(lambda r: r.active)
            ops.write({'active': False})
        return super(ProductProduct, self).write(values)
