# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    promotes = fields.Char(compute="_compute_promotes")
    promoted_by = fields.Char(compute="_compute_promotes")
    cross = fields.Serialized(compute="_compute_promotes")

    @api.depends("product_template_link_ids")
    def _compute_promotes(self):
        # it is useful for display to have both fields as string
        # but for research it is better to have the field as array
        ids = self.ids
        ptype = self.env.ref("alc_product_promoted_links.link_type_promotes")
        domain = [
            "&",
            ("type_id", "=", ptype.id),
            "|",
            ("right_product_tmpl_id", "in", ids),
            ("left_product_tmpl_id", "in", ids),
        ]
        links = self.env["product.template.link"].search(domain)
        for tmpl in self:
            promotes_right = links.filtered(
                lambda pl, pt=tmpl: pl.type_id == ptype
                and pl.right_product_tmpl_id == pt
            )
            promoted_by_ns = promotes_right.mapped("left_product_tmpl_id.display_name")
            tmpl.promoted_by = ",".join(promoted_by_ns)
            tmpl.cross = promoted_by_ns

            promoted_by_left = links.filtered(
                lambda pl, pt=tmpl: pl.type_id == ptype
                and pl.left_product_tmpl_id == pt
            )
            promotes_ns = promoted_by_left.mapped("right_product_tmpl_id.display_name")
            promotes = ",".join(promotes_ns)

            tmpl.promotes = promotes
