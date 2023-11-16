# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.extendable_fastapi import StrictExtendableBaseModel


class ProductDiscountSpecial(StrictExtendableBaseModel):
    id: int
    sequence: int
    date_start: str
    date_end: str

    @classmethod
    def from_product_discount_special(cls, odoo_rec):
        return cls.model_construct(
            id=odoo_rec.id,
            sequence=odoo_rec.sequence,
            date_start=odoo_rec.date_start.isoformat(),
            date_end=odoo_rec.date_end.isoformat(),
        )
