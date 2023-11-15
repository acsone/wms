# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.shopinvader_product.schemas.product import (
    ProductProduct as BaseProductProduct,
)

from .manufacturer import Manufacturer


class ProductProduct(BaseProductProduct, extends=True):
    barcode: str | None = None
    create_date: str
    manufacturer: Manufacturer | None = None

    @classmethod
    def from_product_product(cls, odoo_rec):
        obj = super().from_product_product(odoo_rec)
        obj.barcode = odoo_rec.barcode if odoo_rec.barcode else None
        obj.create_date = odoo_rec.create_date.date().isoformat()
        obj.manufacturer = (
            Manufacturer.from_res_partner(odoo_rec.manufacturer_id)
            if odoo_rec.manufacturer_id
            else None
        )
        return obj
