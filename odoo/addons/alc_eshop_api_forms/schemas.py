# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from __future__ import annotations

from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field

from .models.alc_eshop_form import AlcEshopForm


class Form(BaseModel):
    code: str
    name: str
    form: str
    sequence: int
    form_options: str
    id: int

    @classmethod
    def from_alc_eshop_form(
        cls, record: AlcEshopForm
    ) -> self:  # noqa: F821  pylint: disable=undefined-variable
        return cls(
            code=record.code,
            name=record.name,
            form=record.form,
            sequence=record.sequence,
            form_options=record.form_options,
            id=record.id,
        )


class FormList(BaseModel):
    data: list[Form]
    size: int


class FormSubmitRequest(BaseModel):
    data: Annotated[
        dict[str, str],
        Field(
            description="A key / value mapping ",
            json_schema_extra={"example": {"name": "Mrs B"}},
        ),
    ]


class Status(Enum):
    OK = "OK"


class FormSubmitResponse(BaseModel):
    status: Status | None = None
