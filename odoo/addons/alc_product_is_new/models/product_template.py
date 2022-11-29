# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# Copyright 2022 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    is_new = fields.Boolean(
        related="product_package_storage_type_id.is_new", readonly=True,
    )
    new_product_with_old_date = fields.Boolean(
        default=False,
        compute="_compute_new_product_with_old_date",
        search="_search_new_product_with_old_date",
    )

    product_package_storage_type_id = fields.Many2one(
        "stock.package.storage.type",
        default=lambda self: self.env.ref(
            "alc_stock_storage_type.package_st_M_M_Nouveaute"
        ),
        copy=False,
    )

    def _get_new_products_older_than_a_month(self):
        ids = []
        current_ids = self._get_current_ids()
        self.env.cr.execute(
            """
            SELECT DISTINCT pt.id
                FROM
                        product_template pt
                JOIN stock_package_storage_type pst
                    ON pt.product_package_storage_type_id = pst.id
                WHERE
                        pst.is_new
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
