# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api

from odoo.addons.product.models.product_product import ProductProduct as ProductBase


class ProductProduct(ProductBase):
    @api.depends_context("default_move_type")
    def _compute_partner_ref(self):
        """Called from invoice product onchange.

        As there is a column with product code on the SO/invoice, do not
        put internal code prefix on the line description. This rule applies for
        SO and Invoice at product onchange as invoice line description is
        copied from SO line description.
        """
        if self.env.context.get("default_move_type") in ("out_invoice", "out_refund"):
            for record in self:
                record.partner_ref = record.name
            return None
        return super()._compute_partner_ref()
