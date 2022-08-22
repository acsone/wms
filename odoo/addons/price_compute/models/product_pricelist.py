# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    def _get_rule(self, product, date):
        # this comes basically from _compute_price_rule / Low-level method
        # we don't care about partner or min_qty
        price_categ_id = product.price_category_id.id
        price_category_subquery = "OR item.price_category_id = %(price_categ_id)s"
        price_category_subquery = price_category_subquery if price_categ_id else ""
        query = (
            "SELECT item.id "
            "FROM product_pricelist_item AS item "
            "LEFT JOIN product_category AS categ "
            "ON item.categ_id = categ.id "
            "WHERE (item.product_tmpl_id IS NULL OR item.product_tmpl_id = %(tmpl_id)s)"
            "AND (item.product_id IS NULL OR item.product_id = %(prod_id)s)"
            "AND (item.categ_id IS NULL OR item.categ_id = %(categ_id)s)"
            "AND (categ.parent_left <= %(categ_parent_left)s AND categ.parent_right >= %(categ_parent_right)s) "
            "AND (item.price_category_id IS NULL " + price_category_subquery + ") "
            "AND (item.pricelist_id = %(self_id)s) "
            "AND (item.date_start IS NULL OR item.date_start<=%(date)s) "
            "AND (item.date_end IS NULL OR item.date_end>=%(date)s)"
            "ORDER BY item.applied_on, item.min_quantity desc, categ.parent_left desc"
        )
        query_args = {
            "self_id": self.id,
            "tmpl_id": product.product_tmpl_id.id,
            "prod_id": product.id,
            "categ_id": product.categ_id.id,
            "price_categ_id": price_categ_id,  # might be False
            "date": date,
            "categ_parent_left": product.categ_id.parent_left,
            "categ_parent_right": product.categ_id.parent_right,
        }
        self._cr.execute(query, query_args)  # pylint: disable=sql-injection
        ids = [x[0] for x in self._cr.fetchall()]
        return self.env["product.pricelist.item"].browse(ids[0] if ids else [])
