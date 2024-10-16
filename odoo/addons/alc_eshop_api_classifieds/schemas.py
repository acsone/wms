# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import date
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field

from odoo.addons.alc_eshop_classifieds.models.alc_classified import AlcClassified


class Category(Enum):
    animals = "animals"
    clientele = "clientele"
    employment = "employment"
    equipment = "equipment"
    misc = "misc"


class CountryStateCode(Enum):
    BBR = "BBR"
    VAN = "VAN"
    VBR = "VBR"
    VLI = "VLI"
    VOV = "VOV"
    VWV = "VWV"
    WBR = "WBR"
    WHT = "WHT"
    WLG = "WLG"
    WLX = "WLX"
    WNA = "WNA"


class CountryState(BaseModel):
    code: CountryStateCode
    name: str


class State(Enum):
    draft = "draft"
    cancel = "cancel"
    published = "published"
    pending = "pending"


class ClassifiedAdsCommonData(
    BaseModel,
    revalidate_instances="always",
    validate_assignment=True,
    extra="forbid",
):
    body: str
    category: Category
    name: str
    date_end: date
    date_start: date
    phone: str
    contact: str
    email: str

    @classmethod
    def from_alc_classified(cls, classified: AlcClassified, private=False):
        return cls.model_construct(
            body=classified.body,
            category=Category(classified.category),
            name=classified.name,
            date_end=classified.date_end,
            date_start=classified.date_start,
            phone=classified.phone,
            contact=classified.contact,
            email=classified.email,
        )


class ClassifiedAdsCreate(ClassifiedAdsCommonData, extra="ignore"):
    """Data required to create a classified advertisement."""

    country_state_code: CountryStateCode

    def to_alc_classified_create_vals(self, state_code_to_state: dict[str, id]) -> dict:
        return {
            "body": self.body,
            "category": self.category.value,
            "name": self.name,
            "date_end": self.date_end,
            "date_start": self.date_start,
            "phone": self.phone,
            "contact": self.contact,
            "email": self.email,
            "state_id": (
                state_code_to_state[self.country_state_code.value]
                if self.country_state_code
                else None
            ),
        }


class File(BaseModel):
    url: str
    mimetype: str
    name: str


class ClassifiedAdsUpdate(ClassifiedAdsCommonData, extra="ignore"):
    body: str | None = None
    category: Category | None = None
    name: str | None = None
    date_end: date | None = None
    date_start: date | None = None
    phone: str | None = None
    contact: str | None = None
    email: str | None = None
    country_state_code: CountryStateCode | None = None
    file_delete: bool | None = None

    # flake8: noqa: C901
    def to_alc_classified_update_vals(self, state_code_to_state: dict[str, id]) -> dict:
        values = self.model_dump(exclude_unset=True)
        res = {}
        if "body" in values:
            res["body"] = self.body
        if "category" in values:
            res["category"] = self.category.value
        if "name" in values:
            res["name"] = self.name
        if "date_end" in values:
            res["date_end"] = self.date_end
        if "date_start" in values:
            res["date_start"] = self.date_start
        if "phone" in values:
            res["phone"] = self.phone
        if "contact" in values:
            res["contact"] = self.contact
        if "email" in values:
            res["email"] = self.email
        if "country_state_code" in values:
            res["state_id"] = state_code_to_state[self.country_state_code.value]
        if "file_delete" in values:
            res["file"] = None
        return res


class ClassifiedAds(ClassifiedAdsCommonData):
    """Data related to a classified advertisement."""

    id: int
    country_state: CountryState
    state: Annotated[
        State | None, Field(description="Field only set if the user is the owner")
    ] = None
    rejection_reason: Annotated[
        str | None, Field(description="Field only set if the user is the owner")
    ] = None
    file: File | None = None

    @classmethod
    def from_alc_classified(cls, classified: AlcClassified, private=False):
        instance = super().from_alc_classified(classified, private=private)
        instance.id = classified.id
        instance.country_state = CountryState(
            code=classified.state_id.code, name=classified.state_id.name
        )
        if classified.file:
            instance.file = File(
                url=classified.file.url or classified.file.internal_url,
                mimetype=classified.file.mimetype,
                name=classified.file.name,
            )
        if private:
            instance.state = State(classified.state)
            instance.rejection_reason = classified.rejection_reason or None
        return instance


class ClassifiedAdsSearchParams(ClassifiedAdsUpdate, extra="ignore"):
    from_date: date | None = None


class ClassifiedAdsList(
    BaseModel,
    revalidate_instances="always",
    validate_assignment=True,
    extra="forbid",
):
    """List of classified advertisements."""

    data: list[ClassifiedAds]
    size: int

    @classmethod
    def from_alc_classified(cls, classified: AlcClassified, private=False):
        data = []
        size = 0
        for record in classified:
            size += 1
            data.append(ClassifiedAds.from_alc_classified(record, private))
        return cls(data=data, size=size)
