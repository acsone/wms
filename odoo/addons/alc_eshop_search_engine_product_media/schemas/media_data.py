# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.shopinvader_search_engine_product_media.schemas import (
    MediaData as BaseMediaData,
)


class MediaData(BaseMediaData, extends=True):
    lang: str | None = None

    @classmethod
    def from_media_data(cls, odoo_rec):
        obj = super().from_media_data(odoo_rec)
        obj.lang = odoo_rec.lang if odoo_rec.lang else None
        return obj
