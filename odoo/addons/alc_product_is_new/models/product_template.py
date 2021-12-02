# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    is_new = fields.Boolean(default=False, store=True, compute="_compute_is_new")
    new_product_with_old_date = fields.Boolean(
        default=False,
        compute="_compute_new_product_with_old_date",
        search="_search_new_product_with_old_date",
    )

    @api.depends("product_package_storage_type_id")
    def _compute_is_new(self):
        storage_type_new = self.env.ref(
            "alc_stock_storage_type.package_st_M_M_Nouveaute"
        )
        for product in self:
            product.is_new = product.product_package_storage_type_id == storage_type_new

    def _get_new_products_older_than_a_month(self):
        ids = []
        current_ids = self._get_current_ids()
        self.env.cr.execute(
            """
            SELECT DISTINCT pt.id
                FROM
                        product_template pt
                WHERE
                        pt.is_new
                    AND pt.create_date < NOW() - '1 month'::interval
                %(ids)s
            """,
            {"ids": current_ids},
        )
        result = self.env.cr.fetchall()
        ids = [r[0] for r in result]
        return ids

    @api.depends("is_new")
    def _compute_new_product_with_old_date(self):
        ids_new_products_old_date = set(self._get_new_products_older_than_a_month())
        for product in self:
            product.new_product_with_old_date = product.id in ids_new_products_old_date

    def _search_new_product_with_old_date(self, operator, value):
        ids = self._get_new_products_older_than_a_month()
        return [("id", "in", ids)]
