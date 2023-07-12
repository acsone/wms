# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import Generic, TypeVar

from pydantic.generics import GenericModel

T = TypeVar("T")


class PagedCollection(GenericModel, Generic[T]):

    size: int
    data: list[T]
