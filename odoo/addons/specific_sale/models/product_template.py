# -*- coding: utf-8 -*-
# © 2017 Julien Coux (Camptocamp)
# © 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import ast

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    sale_lines_count = fields.Integer(compute="_compute_sale_lines_count")

    @api.multi
    @api.depends("product_variant_ids.sales_count")
    def _compute_sale_lines_count(self):
        for product in self:
            product.sale_lines_count = sum(
                [p.sale_lines_count for p in product.product_variant_ids]
            )

    @api.multi
    def action_view_sale_lines_unavailable(self):
        self.ensure_one()

        action_data = self.env.ref(
            "specific_sale.action_sale_lines_unavailable_list"
        ).read()[0]
        action_data["domain"] = [
            ("state", "in", ["sale"]),
            ("product_id.product_tmpl_id", "=", self.id),
        ]

        return action_data

    @api.multi
    def action_view_sales(self):
        res = super(ProductTemplate, self).action_view_sales()
        if res["context"]:
            action_context = ast.literal_eval(res["context"])
            action_context["search_default_remains_to_deliver"] = 1
            res["context"] = str(action_context)
        else:
            res["context"] = "{'search_default_remains_to_deliver': 1,}"
        return res
