# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.shopinvader_product.schemas.product import (
    ProductProduct as BaseProductProduct,
)

from .account_tax import AccountTax


class ProductProduct(BaseProductProduct, extends=True):
    taxes_id: list[str] = []
    vat: AccountTax | None = None

    @classmethod
    def from_product_product(cls, odoo_rec):
        obj = super().from_product_product(odoo_rec)
        obj.taxes_id = (
            odoo_rec.taxes_id.mapped("display_name") if odoo_rec.taxes_id else []
        )
        obj.vat = (
            AccountTax.from_account_tax(odoo_rec.vat_id) if odoo_rec.vat_id else None
        )
        return obj
