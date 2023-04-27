from fastapi.security import APIKeyHeader
from odoo.addons.fastapi.schemas import GenericModel, Generic
from typing import List, TypeVar
from pydantic import BaseModel as PydanticBaseModel

T = TypeVar("T")


class PagedCollection(GenericModel, Generic[T]):

    size: int
    data: List[T]


class BaseModel(PydanticBaseModel):
    def _convert_to_write(self):
        values = self.dict()
        return {field: values[field] for field in self.__fields_set__}


api_key_header = APIKeyHeader(
    name="api-key",
    description="In this demo, you can use a user's login as api key.",
)
