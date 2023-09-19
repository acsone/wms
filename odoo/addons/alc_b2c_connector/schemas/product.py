# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo.addons.product.models.product_product import ProductProduct

from . import tax
from .base_model import BaseModel


class Product(BaseModel):
    sku: str | None
    create_date: datetime
    name: str
    price: float
    eans: list[str] | None
    cnk: str | None
    taxes: list[tax.Tax] | None
    quantity: float

    @classmethod
    def from_product_product(cls, product: ProductProduct) -> "Product":
        return cls.model_construct(
            sku=product.default_code or None,
            create_date=product.create_date,
            name=product.name,
            price=product.list_price,
            eans=[product.barcode] if product.barcode else [],
            cnk=product.cnk_code or None,
            taxes=[tax.Tax.from_account_tax(tax_) for tax_ in product.taxes_id],
            quantity=product.immediately_usable_qty,
        )
