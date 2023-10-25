# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from extendable_pydantic import StrictExtendableBaseModel


class AlcEshopAds(StrictExtendableBaseModel):

    id: int
    allowed_roles: str
    name: str
    date_start: str
    date_end: str
    site_url: str
    display_time: int
    display_slot: str
    file: str | None = None
    image: str | None = None

    @classmethod
    def from_eshop_ads(cls, odoo_rec):
        return cls.model_construct(
            id=odoo_rec.id,
            allowed_roles=",".join(odoo_rec._compute_security()),
            name=odoo_rec.name,
            date_start=odoo_rec.date_start.isoformat(),
            date_end=odoo_rec.date_end.isoformat(),
            site_url=odoo_rec.site_url or "",
            display_time=odoo_rec.display_time,
            display_slot=odoo_rec.display_slot,
            file=None,
            image=None,
        )
