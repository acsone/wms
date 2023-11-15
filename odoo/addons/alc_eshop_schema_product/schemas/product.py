# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.shopinvader_product.schemas.product import (
    ProductProduct as BaseProductProduct,
)


class ProductProduct(BaseProductProduct, extends=True):
    barcode: str | None = None
    create_date: str

    @classmethod
    def from_product_product(cls, odoo_rec):
        obj = super().from_product_product(odoo_rec)
        obj.barcode = odoo_rec.barcode if odoo_rec.barcode else None
        obj.create_date = odoo_rec.create_date.date().isoformat()
        return obj
