# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.extendable_fastapi import StrictExtendableBaseModel


class ProductStorageTemperature(StrictExtendableBaseModel):
    id: int
    name: str | None = None

    @classmethod
    def from_product_storage_temperature(cls, odoo_rec):
        return cls.model_construct(id=odoo_rec.id, name=odoo_rec.name or None)
