# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.shopinvader_product.schemas.product import (
    ProductProduct as BaseProductProduct,
)


class ProductProduct(BaseProductProduct, extends=True):
    is_meds: bool | None = None
    is_equipment: bool | None = None
    is_psychotropic: bool | None = None
    is_pharmaceutical: bool | None = None
    is_import: bool | None = None
    is_narcotic_vet: bool | None = None
    is_human: bool | None = None
    belgium_only: bool | None = None
    veterinary_only: bool | None = None
    cnk_code: str | None = None
    code_cti: str | None = None
    code_amm: str | None = None

    @classmethod
    def from_product_product(cls, odoo_rec):
        obj = super().from_product_product(odoo_rec)
        obj.is_meds = odoo_rec.is_meds
        obj.is_equipment = odoo_rec.is_equipment
        obj.is_psychotropic = odoo_rec.is_psychotropic
        obj.is_pharmaceutical = odoo_rec.is_pharmaceutical
        obj.is_import = odoo_rec.is_import
        obj.is_narcotic_vet = odoo_rec.is_narcotic_vet
        obj.is_human = odoo_rec.is_human
        obj.belgium_only = odoo_rec.belgium_only
        obj.veterinary_only = odoo_rec.veterinary_only
        obj.cnk_code = odoo_rec.cnk_code if odoo_rec.cnk_code else None
        obj.code_cti = odoo_rec.code_cti if odoo_rec.code_cti else None
        obj.code_amm = odoo_rec.code_amm if odoo_rec.code_amm else None
        return obj
