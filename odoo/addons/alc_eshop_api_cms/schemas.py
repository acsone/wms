# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from __future__ import annotations

from enum import Enum
from typing import Annotated, Literal

from pydantic import BaseModel, Field

from odoo.addons.alc_eshop_cms.models import (
    AlcContentLangMixin,
    AlcEshopCmsPage,
    AlcEshopCmsSnippet,
)


class ContentLang(Enum):
    nl = "nl"
    en = "en"
    fr = "fr"
    de = "de"


class ContentType(Enum):
    page = "page"
    news = "news"
    snippet = "snippet"


class ContentSearchParams(BaseModel, extra="ignore"):
    lang: ContentLang | None = None
    type: ContentType | None = None


class ContentBase(
    BaseModel,
    revalidate_instances="always",
    validate_assignment=True,
    extra="forbid",
):
    lang: ContentLang
    url: str
    url_locales: dict[str, str] = Field(
        ...,
        description="A lang / url mapping ",
        json_schema_extra={
            "example": {
                "fr": "/fr/snippet/mon-frag-1",
                "en": "/en/snippet/my-snippet-1",
            }
        },
    )
    type: ContentType
    id: int

    @classmethod
    def from_odoo_record(
        cls, record: AlcContentLangMixin
    ) -> self:  # noqa: F821  pylint: disable=undefined-variable
        instance = cls.model_construct(
            lang=record._get_content_context_lang(),
            url=record._get_content_url(),
            url_locales=record._get_content_url_locales(),
            id=record.id,
            type=record._content_type,
        )
        return instance


class Image(
    BaseModel,
    revalidate_instances="always",
    validate_assignment=True,
    extra="forbid",
):
    url: str
    alt_name: str | None
    name: str


class File(
    BaseModel,
    revalidate_instances="always",
    validate_assignment=True,
    extra="forbid",
):
    url: str
    name: str
    mimetype: str


class News(
    BaseModel,
    revalidate_instances="always",
    validate_assignment=True,
    extra="forbid",
):
    type: Literal["news"] = "news"
    title: str
    foreword: str
    content: str
    thumbnail: Image | None = None
    image: Image | None = None
    file: File | None = None

    @classmethod
    def from_odoo_record(
        cls, record: AlcEshopCmsPage
    ) -> self:  # noqa: F821  pylint: disable=undefined-variable
        instance = cls.model_construct(
            title=record.name,
            foreword=record.foreword,
            content=record.content,
        )
        if record.thumbnail_image:
            instance.thumbnail = Image(
                url=record.thumbnail_image.url,
                alt_name=record.thumbnail_image.alt_text or None,
                name=record.thumbnail_image.name,
            )
        if record.image:
            instance.image = Image(
                url=record.image.url,
                alt_name=record.image.alt_text or None,
                name=record.image.name,
            )
        if record.file:
            instance.file = File(
                url=record.file.url,
                name=record.file.name,
                mimetype=record.file.mimetype,
            )
        return instance


class Page(
    BaseModel,
    revalidate_instances="always",
    validate_assignment=True,
    extra="forbid",
):
    type: Literal["page"] = "page"
    title: str
    content: str
    sequence: int = 0
    group: str
    slots: list[str]

    @classmethod
    def from_odoo_record(
        cls, record: AlcEshopCmsPage
    ) -> self:  # noqa: F821  pylint: disable=undefined-variable
        instance = cls.model_construct(
            title=record.name,
            content=record._get_content(),
            sequence=record.sequence,
            group=record.cms_page_group_id.name,
            slots=record.cms_page_slot_ids.mapped("name"),
        )
        return instance


class Snippet(
    BaseModel,
    revalidate_instances="always",
    validate_assignment=True,
    extra="forbid",
):
    type: Literal["snippet"] = "snippet"
    code: str
    content: str

    @classmethod
    def from_odoo_record(
        cls, record: AlcEshopCmsSnippet
    ) -> self:  # noqa: F821 pylint: disable=undefined-variable
        instance = cls.model_construct(
            code=record.code,
            content=record._get_content(),
        )
        return instance


class Content(ContentBase):
    data: Annotated[News | Page | Snippet, Field(discriminator="type")]

    @classmethod
    def from_odoo_record(
        cls, record
    ) -> self:  # noqa: F821  pylint: disable=undefined-variable
        instance = super().from_odoo_record(record)
        if record._content_type == "news":
            instance.data = News.from_odoo_record(record)
        elif record._content_type == "page":
            instance.data = Page.from_odoo_record(record)
        elif record._content_type == "snippet":
            instance.data = Snippet.from_odoo_record(record)
        return instance


class ContentList(
    BaseModel,
    revalidate_instances="always",
    validate_assignment=True,
    extra="forbid",
):
    size: int
    data: list[Content]
