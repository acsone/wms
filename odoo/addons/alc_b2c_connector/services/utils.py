from enum import Enum
from typing import TypeVar

from fastapi.security import APIKeyHeader
from pydantic import BaseModel as PydanticBaseModel

from odoo.addons.fastapi.schemas import Generic, GenericModel

T = TypeVar("T")


class PagedCollection(GenericModel, Generic[T]):

    size: int
    data: list[T]


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


api_key_header = APIKeyHeader(
    name="api-key",
    description="In this demo, you can use a user's login as api key.",
)
