# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from typing import Annotated

from fastapi import APIRouter, Depends

from odoo import api

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.fastapi.dependencies import (
    optionally_authenticated_partner,
    optionally_authenticated_partner_env,
)

from ..schemas import Form, FormList, FormSubmitRequest, FormSubmitResponse

forms_router = APIRouter(tags=["forms"])


@forms_router.get("/form", deprecated=True, description="Use /forms instead")
@forms_router.get("/forms")
def get_all_forms(
    env: Annotated[api.Environment, Depends(optionally_authenticated_partner_env)],
    partner: Annotated[
        Partner | None, Depends(optionally_authenticated_partner)
    ] = None,
) -> FormList:
    audience = "authenticated_only" if partner else "public_only"
    forms = (
        env["alc.eshop.form"]
        .sudo()
        .search([("audience", "=", audience), ("published", "=", True)])
    )
    return FormList(size=len(forms), data=[Form.from_alc_eshop_form(f) for f in forms])


@forms_router.post("/form/{form_id}", deprecated=True, description="Use /forms instead")
@forms_router.post("/forms/{form_id}")
def submit_form(
    env: Annotated[api.Environment, Depends(optionally_authenticated_partner_env)],
    form_id: int,
    body: FormSubmitRequest,
    partner: Annotated[
        Partner | None, Depends(optionally_authenticated_partner)
    ] = None,
) -> FormSubmitResponse:
    form = env["alc.eshop.form"].sudo().browse(form_id).exists()
    form._send_collected_info(body.data, partner)
    return FormSubmitResponse(status="OK")
