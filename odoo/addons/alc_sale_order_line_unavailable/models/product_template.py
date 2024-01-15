# © 2017 Julien Coux (Camptocamp)
# © 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.product.models.product_template import (
    ProductTemplate as ProductTemplateBase,
)

from .mixin_sales_lines_unavailable_action import MixinSaleLinesUnavailableAction


class ProductTemplate(ProductTemplateBase, MixinSaleLinesUnavailableAction):
    _name = "product.template"

    def _get_view_sale_lines_unavailable_record_id_domain(self):
        self.ensure_one()
        return [("product_id.product_tmpl_id", "=", self.id)]
