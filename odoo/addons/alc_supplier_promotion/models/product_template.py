# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.product.models.product_template import (
    ProductTemplate as ProductTemplateBase,
)

from .product_supplierinfo import ProductSupplierInfo


class ProductTemplate(ProductTemplateBase):

    supplier_promotion_ids = fields.One2many[ProductSupplierInfo](
        compute="_compute_seller_ids_subfields"
    )
    supplier_discount_ids = fields.One2many[ProductSupplierInfo](
        compute="_compute_seller_ids_subfields"
    )

    @api.depends("seller_ids")
    def _compute_seller_ids_subfields(self):
        for product in self:
            current_info = product.seller_ids.filtered(lambda si: not si.is_past)
            product.supplier_promotion_ids = current_info.filtered("is_promotion")
            product.supplier_discount_ids = current_info.filtered("is_sale_discount")

    def get_promotional_product(self, qty, uom):
        """Compute how many promotional product are offered.

        Given a quantity and a unity of measure, returns for the current
        day how many promotional (free) product will be given.
        The unit of measure is adapted if needs be.
        """
        self.ensure_one()
        if uom != self.uom_id:
            qty = uom._compute_quantity(qty, self.uom_id)
        result = self.env["product.supplierinfo"].search(
            [
                ("ratio_promotional_product", ">", 0),
                ("ratio_main_product", ">", 0),
                "|",
                ("date_start", "=", False),
                ("date_start", "<=", fields.Date.today()),
                "|",
                ("date_end", "=", False),
                ("date_end", ">=", fields.Date.today()),
                "|",
                ("min_qty_sale", "=", False),
                ("min_qty_sale", "<=", qty),
                ("product_tmpl_id", "=", self.id),
            ],
            order="sequence, min_qty_sale desc, price",
            limit=1,
        )
        if not result:
            return 0
        coefficient = int(qty / result.ratio_main_product)
        return coefficient * result.ratio_promotional_product
