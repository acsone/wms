# © 2017 Julien Coux (Camptocamp)
# © 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.product.models.product_template import (
    ProductTemplate as ProductTemplateBase,
)


class ProductTemplate(ProductTemplateBase):
    def action_view_sale_lines_unavailable(self):
        self.ensure_one()

        action_data = self.env.ref(
            "alc_sale_order_line_unavailable_list.action_sale_order_line_unavailable_list"
        ).read()[0]
        action_data["domain"] = [
            ("state", "in", ["sale", "done"]),
            ("product_id.product_tmpl_id", "=", self.id),
        ]

        return action_data
