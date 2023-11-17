# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.shopinvader_product.schemas.product import (
    ProductProduct as BaseProductProduct,
)


class ProductProduct(BaseProductProduct, extends=True):
    vendor_product_code: str | None = None
    supplier_id: int | None = None

    @classmethod
    def from_product_product(cls, odoo_rec):
        obj = super().from_product_product(odoo_rec)
        obj.vendor_product_code = (
            odoo_rec.vendor_product_code if odoo_rec.vendor_product_code else None
        )
        obj.supplier_id = odoo_rec.supplier_rel_id if odoo_rec.supplier_rel_id else None
        return obj
