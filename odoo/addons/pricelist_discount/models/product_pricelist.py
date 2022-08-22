# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist"

    @api.model
    def _get_discount_item_id(self, product, date):
        """Returns the id of the best discount item"""
        discount_item_id = False
        price_categ_id = product.price_category_id.id
        subquery = " OR item.price_category_id = %(price_categ_id)s "
        subquery = subquery if price_categ_id else ""
        query_args = {
            "pl_ids": tuple(self.ids),
            "tmpl_id": product.product_tmpl_id.id,
            "prod_id": product.id,
            "categ_id": product.categ_id.id,
            "price_categ_id": price_categ_id,  # might be False
            "date": date,
            "categ_parent_left": product.categ_id.parent_left,
            "categ_parent_right": product.categ_id.parent_right,
        }
        query = (
            """
SELECT DISTINCT ON (pricelist_id)
       item.id, compute_price, item.percent_price, pricelist_id
FROM product_pricelist_item AS item
LEFT JOIN product_category AS categ
ON item.categ_id = categ.id
WHERE (item.product_tmpl_id IS NULL OR item.product_tmpl_id = %(tmpl_id)s)
AND (item.product_id IS NULL OR item.product_id = %(prod_id)s)
AND (item.categ_id IS NULL OR item.categ_id = %(categ_id)s)
AND (categ.parent_left <= %(categ_parent_left)s AND categ.parent_right >= %(categ_parent_right)s)
AND (item.price_category_id IS NULL"""
            + subquery
            + """)
AND (item.pricelist_id in %(pl_ids)s)
AND (item.date_start IS NULL OR item.date_start<=%(date)s)
AND (item.date_end IS NULL OR item.date_end>=%(date)s)
ORDER BY pricelist_id, item.applied_on, item.min_quantity desc, categ.parent_left desc
"""
        )
        # pylint: disable=sql-injection
        self.env.cr.execute(query, query_args)
        res = self.env.cr.fetchall()
        if res:
            # almost all discounts are given in percent
            if all(r[1] == "percentage" for r in res):
                # in that case, the best is simply the best discount
                discount_item_id = max(res, key=lambda r: r[2])[0]
            else:
                # here we could distinguish more subcases, e.g. all fixed price
                # however given how rare the case is, it is not worth it.
                item_ids = [r[0] for r in res]
                items = self.env["product.pricelist.item"].browse(item_ids)
                # another hypothesis: we only allow discount based on base price
                # assert(all(item.base == "list_price" for item in items))
                price_unit = product.lst_price
                get_price = lambda r, p=price_unit: r._compute_price(p)
                discount_item_id = min(items, key=get_price).id
        return discount_item_id
