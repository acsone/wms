# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.search_engine_serializer_pydantic.tools.serializer import (
    PydanticModelSerializer,
)

from ..schemas import AlcEshopInfoBanner


class AlcEshopInfoBannerShopinvaderSerializer(PydanticModelSerializer):
    def get_model_class(self):
        return AlcEshopInfoBanner

    def serialize(self, record):
        return self.get_model_class().from_eshop_info_banner(record).model_dump()
