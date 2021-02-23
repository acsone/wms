# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductProduct(models.Model):

    _inherit = "product.product"
    business_unit_id = fields.Many2one(
        "product.category",
        string="Business unit",
        compute="_compute_business_unit_id",
        readonly=True,
        store=True,
    )

    @api.depends("categ_id")
    def _compute_business_unit_id(self):
        business_units = self.env["product.category"].search(
            [("is_business_unit", "=", True)]
        )

        # If there is business units, we can stop this method now
        # to avoid to loop on each product for nothing
        if not business_units:
            return

        bu_by_categ = {}
        for business_unit in business_units:
            business_unit_id = business_unit.id
            bu_by_categ[business_unit_id] = business_unit_id
            children_categ_query = """
            WITH RECURSIVE tree AS (
              SELECT id, ARRAY[]::INTEGER[] AS ancestors
              FROM product_category WHERE parent_id IS NULL

              UNION ALL

              SELECT
                product_category.id,
                tree.ancestors || product_category.parent_id
              FROM product_category, tree
              WHERE product_category.parent_id = tree.id
            ) SELECT id FROM tree WHERE %s = ANY(tree.ancestors);
            """
            self.env.cr.execute(children_categ_query, (business_unit.id,))

            for categ in self.env.cr.fetchall():
                bu_by_categ[categ[0]] = business_unit_id

        for product in self:
            if not product.categ_id or product.categ_id.id not in bu_by_categ:
                product.business_unit_id = None
            else:
                product.business_unit_id = bu_by_categ[product.categ_id.id]
