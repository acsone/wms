# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import mimetypes
from datetime import datetime
from typing import Annotated

import pytz
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse

from odoo import api
from odoo.http import content_disposition

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
)

from ..schemas import DocumentList, DocumentType, SaleChannel

documents_router = APIRouter(tags=["documents"])


@documents_router.get("/documents/{_id}/download")
def download(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[Partner, Depends(authenticated_partner)],
    _id: int,
) -> FileResponse:
    """Download a document.

    This endpoint is used to download a document. The response is a file in
    the mimetype of the document.
    """
    model = env["alc.document"]
    domain = model.get_partner_domain(partner)
    domain.append(("id", "=", _id))
    document = model.sudo().search(domain, limit=1)
    if not document:
        raise HTTPException(status_code=404, detail=f"Document with id {_id} not found")
    attachment = document._get_attachment()

    def stream(chunk_size: int = 4096):
        with attachment.open("rb") as f:
            chunk = f.read(chunk_size)
            while chunk:
                yield chunk
                chunk = f.read(chunk_size)

    header = {
        "Content-Disposition": content_disposition(document.name),
    }
    mimetype_guess = mimetypes.guess_type(document.name)
    mimetype = mimetype_guess[0] if mimetype_guess else mimetype_guess
    return StreamingResponse(stream(), headers=header, media_type=mimetype)


@documents_router.get("/documents/", status_code=200)
def search(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[Partner, Depends(authenticated_partner)],
    document_type: Annotated[DocumentType | None, Query(alias="type")] = None,
    sale_channel: SaleChannel | None = None,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    page: int | None = 1,
    per_page: int | None = 10,
) -> DocumentList:
    """Search documents."""
    model = env["alc.document"]
    domain = model.get_partner_domain(partner)
    if document_type:
        domain.append(("type", "=", document_type.value))
    if sale_channel:
        channel_id = env["sale.channel"].sudo()._get_id_from_code(sale_channel.value)
        domain.append(("sale_channel_id", "=", channel_id))
    if from_date:
        from_date = from_date.astimezone(pytz.timezone("UTC"))
        domain.append(("document_date", ">=", from_date))
    if to_date:
        to_date = to_date.astimezone(pytz.timezone("UTC"))
        domain.append(("document_date", "<=", to_date))
    total_count = model.sudo().search_count(domain)
    offset = per_page * (page - 1)
    records = model.search(domain, limit=per_page, offset=offset)
    response = DocumentList.from_alc_document(records)
    response.size = total_count
    return response
