# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from enum import Enum

from pydantic import BaseModel as PydanticBaseModel


class BaseModel(PydanticBaseModel):
    def _convert_to_write_field(self, field):
        if isinstance(field, BaseModel):
            return field._convert_to_write()
        if isinstance(field, Enum):
            return field.value
        return field

    def _convert_to_write(self):
        values = dict(self)
        res = {}
        for field in self.__fields_set__:
            value = values[field]
            if isinstance(value, list):
                value = [self._convert_to_write_field(el) for el in value]
            else:
                value = self._convert_to_write_field(value)
            res[field] = value
        return res
