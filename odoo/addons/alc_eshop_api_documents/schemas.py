# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel

from odoo.addons.alc_cerberus_utils import utils
from odoo.addons.alc_documents.models.alc_document import AlcDocument


class DocumentType(Enum):
    order = "order"
    delivery_note = "delivery_note"
    invoice = "invoice"
    credit_note = "credit_note"
    pricelist = "pricelist"
    discount = "discount"


class SaleChannel(Enum):
    phone = "phone"
    mail = "mail"
    fax = "fax"
    web = "web"


class Document(
    BaseModel, revalidate_instances="always", validate_assignment=True, extra="forbid"
):
    name: str
    format: str
    res_model: str | None = None
    sale_channel: SaleChannel | None = None
    type: str
    id: int
    document_date: datetime | None = None

    @classmethod
    def from_alc_document(
        cls, alc_document: AlcDocument
    ) -> self:  # noqa: F821  pylint: disable=undefined-variable
        document_date = None
        if alc_document.document_date:
            document_date = utils.odoo_dt_to_dt_utc(alc_document.document_date)
        return cls(
            name=alc_document.name,
            format=alc_document.format,
            res_model=alc_document.res_model or None,
            sale_channel=alc_document.sale_channel_id.code or None,
            type=alc_document.type,
            id=alc_document.id,
            document_date=document_date,
        )


class DocumentList(BaseModel):
    data: list[Document]
    size: int

    @classmethod
    def from_alc_document(
        cls, alc_document: AlcDocument
    ) -> self:  # noqa: F821  pylint: disable=undefined-variable
        data = [Document.from_alc_document(document) for document in alc_document]
        return cls(
            data=data,
            size=len(data),
        )
