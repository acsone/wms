from fastapi.security import APIKeyHeader
from odoo.addons.fastapi.schemas import GenericModel, Generic
from typing import List, TypeVar


T = TypeVar("T")


class PagedCollection(GenericModel, Generic[T]):

    size: int
    data: List[T]


api_key_header = APIKeyHeader(
    name="api-key",
    description="In this demo, you can use a user's login as api key.",
)
