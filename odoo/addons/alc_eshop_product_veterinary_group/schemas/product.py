# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.shopinvader_product.schemas.product import (
    ProductProduct as BaseProductProduct,
)

from .veterinary_group import VeterinaryGroup


class ProductProduct(BaseProductProduct, extends=True):
    veterinary_groups: list[VeterinaryGroup] = []
    vt_groups: dict[int, str] = {}

    @classmethod
    def from_product_product(cls, odoo_rec):
        obj = super().from_product_product(odoo_rec)
        obj.veterinary_groups = (
            [
                VeterinaryGroup.from_veterinary_group(vg)
                for vg in odoo_rec.veterinary_group_ids
            ]
            if odoo_rec.veterinary_group_ids
            else []
        )
        obj.vt_groups = odoo_rec.vt_groups if odoo_rec.vt_groups else {}
        return obj
