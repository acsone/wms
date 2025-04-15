# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.search_engine_serializer_pydantic.tools.serializer import (
    PydanticModelSerializer,
)

from ..schemas import LoyaltyProgram


class LoyaltyProgramSerializer(PydanticModelSerializer):
    def get_model_class(self):
        return LoyaltyProgram

    def serialize(self, record):
        return (
            self.get_model_class().from_loyalty_program(record).model_dump(mode="json")
        )
