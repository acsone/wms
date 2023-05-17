# Copyright 2023 ASCONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.product.models.product_product import ProductProduct as ProductBase


class ProductProduct(ProductBase):
    def _compute_sales_count(self):
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
        self._cr.execute(query, (tuple(self.ids),))

        done = {}
        res = self._cr.fetchall()
        if not res:
            self.sales_count = False
            return
        product_ids = {so[0] for so in res}
        without_sale_count = self.filtered(lambda x: x.id not in product_ids)
        without_sale_count.sales_count = False
        for product_id, qty, state in res:
            product = self.browse(product_id)
            if state == "sale":
                product.sale_lines_count = qty
            elif state == "done":
                done[product_id] = qty
            product.sales_count = product.sale_lines_count + done.get(product_id, 0)

    # override compute of sales_count for perf...
    sales_count = fields.Integer(compute="_compute_sales_count")
    sale_lines_count = fields.Integer(compute="_compute_sales_count")
