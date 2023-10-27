# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel

from odoo.addons.alc_product_flattened_data.models.alc_product_flattened_data import (
    AlcProductFlattenedData,
)


class ProductBrand(BaseModel):
    id: int
    name: str


class ProductBrandList(BaseModel):
    data: list[ProductBrand]
    size: int


class Product(BaseModel):
    category: str
    indicated_price: float
    name: str
    reference: str
    ext_cti: str | None
    ean_13: str | None
    code_amm: str | None
    price_tvac: float
    price_htva: float
    cnk_code: str | None
    vat: float
    manufacturer: str | None

    @classmethod
    def from_product_flattened_data(cls, record: AlcProductFlattenedData):
        price_htva = record.gross_price
        vat = record.tax_amount
        return cls(
            category=record.categ,
            indicated_price=record.indicated_price,
            name=record.name,
            reference=record.default_code,
            ext_cti=record.code_cti or None,
            ean_13=record.barcode or None,
            code_amm=record.code_amm or None,
            price_tvac=price_htva + (price_htva * vat / 100),
            price_htva=price_htva,
            cnk_code=record.cnk_code or None,
            vat=vat,
            manufacturer=record.manufacturer or None,
        )


class Lang(Enum):
    en = "en"
    fr = "fr"
    nl = "nl"


class ProductList(BaseModel):
    data: list[Product]
    size: int
