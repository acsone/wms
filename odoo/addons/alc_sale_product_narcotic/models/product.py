# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields

from odoo.addons.sale.models.product_template import (
    ProductTemplate as ProductTemplateBase,
)

WARNING = "warning"
WARNING_MSG = _("A narcotic voucher is required for the data entry.")


class ProductTemplate(ProductTemplateBase):

    sale_line_warn = fields.Selection(
        compute="_compute_sale_line_warn", readonly=False, store=True
    )
    sale_line_warn_msg = fields.Text(
        compute="_compute_sale_line_warn", readonly=False, store=True
    )

    @api.depends("is_narcotic_reg", "is_narcotic_vet")
    def _compute_sale_line_warn(self):
        for product in self:
            if product.is_narcotic_reg or product.is_narcotic_vet:
                product.sale_line_warn = WARNING
                product.sale_line_warn_msg = WARNING_MSG
