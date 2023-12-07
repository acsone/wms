# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from __future__ import annotations

from datetime import date

from extendable_pydantic import StrictExtendableBaseModel


class AdsImage(StrictExtendableBaseModel):
    name: str
    url: str

    @classmethod
    def from_odoo_field(
        cls, image
    ) -> self | None:  # noqa: F821  pylint: disable=undefined-variable
        if not image:
            return None
        return cls.model_construct(
            name=image.name,
            url=image.url,
        )


class AdsFile(StrictExtendableBaseModel):
    name: str
    url: str
    mimetype: str | None

    @classmethod
    def from_odoo_field(
        cls, file
    ) -> self | None:  # noqa: F821  pylint: disable=undefined-variable
        if not file:
            return None
        return cls.model_construct(
            name=file.name,
            url=file.url,
            mimetype=file.mimetype or None,
        )


class AlcEshopAds(StrictExtendableBaseModel):

    id: int
    allowed_roles: str
    name: str
    date_start: date
    date_end: date
    site_url: str
    display_time: int
    display_slot: str
    file: AdsFile | None = None
    image: AdsImage | None = None

    @classmethod
    def from_eshop_ads(cls, odoo_rec):
        return cls.model_construct(
            id=odoo_rec.id,
            allowed_roles=",".join(odoo_rec._compute_security()),
            name=odoo_rec.name,
            date_start=odoo_rec.date_start,
            date_end=odoo_rec.date_end,
            site_url=odoo_rec.site_url or "",
            display_time=odoo_rec.display_time,
            display_slot=odoo_rec.display_slot,
            file=AdsFile.from_odoo_field(odoo_rec.file),
            image=AdsImage.from_odoo_field(odoo_rec.image),
        )
