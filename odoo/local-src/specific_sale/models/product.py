# -*- coding: utf-8 -*-
# © 2017 Julien Coux (Camptocamp)
# © 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api, fields


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def _sales_count(self):
        # rewrite of method as sale.report is very slow to load
        query = """
            SELECT
                product_id,
                sum ("sale_order_line"."product_uom_qty") AS "product_uom_qty",
                state
                FROM sale_order_line
                WHERE state in ('sale', 'done')
                    AND product_id in %s
                GROUP BY product_id, state
                """
        self._cr.execute(query, (tuple(self.ids), ))

        done = {}
        for product_id, qty, state in self._cr.fetchall():
            product = self.browse(product_id)
            if state == 'sale':
                product.sale_lines_count = qty
            elif state == 'done':
                done[product_id] = qty
            product.sales_count = (product.sale_lines_count +
                                   done.get(product_id, 0))

    sale_lines_count = fields.Integer(
        compute='_sales_count'
    )


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sale_lines_count = fields.Integer(
        compute='_compute_sale_lines_count'
    )

    @api.multi
    @api.depends('product_variant_ids.sales_count')
    def _compute_sale_lines_count(self):
        for product in self:
            product.sale_lines_count = sum(
                [p.sale_lines_count for p in product.product_variant_ids])

    @api.multi
    def action_view_sale_lines_unavailable(self):
        self.ensure_one()

        action_data = self.env.ref(
            'specific_sale.action_sale_lines_unavailable_list'
        ).read()[0]
        action_data['domain'] = [
            ('state', 'in', ['sale']),
            ('product_id.product_tmpl_id', '=', self.id)
        ]

        return action_data
