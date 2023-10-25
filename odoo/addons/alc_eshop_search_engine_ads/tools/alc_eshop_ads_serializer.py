# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.search_engine_serializer_pydantic.tools.serializer import (
    PydanticModelSerializer,
)

from ..schemas import AlcEshopAds


class AlcEshopAdsSerializer(PydanticModelSerializer):
    def get_model_class(self):
        return AlcEshopAds

    def serialize(self, record):
        return self.get_model_class().from_eshop_ads(record).model_dump()
