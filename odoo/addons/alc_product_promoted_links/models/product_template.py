# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.base_sparse_field.models.fields import Serialized
from odoo.addons.product_template_multi_link.models.product_template import (
    ProductTemplate as ProductTemplateBase,
)


class ProductTemplate(ProductTemplateBase):

    promotes = fields.Char(compute="_compute_promotes")
    promoted_by = fields.Char(compute="_compute_promotes")
    cross = Serialized(compute="_compute_promotes")

    def _get_promoted_links_domain(self):
        ptype = self.env.ref("alc_product_promoted_links.link_type_promotes")
        return [
            "&",
            ("type_id", "=", ptype.id),
            "|",
            ("right_product_tmpl_id", "in", self.ids),
            ("left_product_tmpl_id", "in", self.ids),
        ]

    @api.depends("product_template_link_ids")
    def _compute_promotes(self):
        """
        It is useful for display to have both fields as string.

        but for research it is better to have the field as array
        """
        links = self.env["product.template.link"].search(
            self._get_promoted_links_domain()
        )
        for tmpl in self:
            promotes_right = links.filtered(
                lambda pl, pt=tmpl: pl.right_product_tmpl_id == pt
            )
            promoted_by_left = links.filtered(
                lambda pl, pt=tmpl: pl.left_product_tmpl_id == pt
            )
            promoted_by_ns = promotes_right.mapped("left_product_tmpl_id.display_name")
            tmpl.promoted_by = ",".join(promoted_by_ns)
            tmpl.cross = promoted_by_ns
            promotes_ns = promoted_by_left.mapped("right_product_tmpl_id.display_name")
            promotes = ",".join(promotes_ns)
            tmpl.promotes = promotes
