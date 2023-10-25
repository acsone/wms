# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from extendable_pydantic import StrictExtendableBaseModel


class AlcEshopInfoBanner(StrictExtendableBaseModel):
    id: int
    html: str
    date_start: str
    date_end: str
    type: str
    visibility: str

    @classmethod
    def from_eshop_info_banner(cls, odoo_rec):
        return cls.model_construct(
            id=odoo_rec.id,
            html=odoo_rec.html,
            date_start=odoo_rec.date_start.isoformat(),
            date_end=odoo_rec.date_end.isoformat(),
            type=odoo_rec.type,
            visibility=odoo_rec.visibility,
        )
