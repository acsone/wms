# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile
from fastapi.params import Form
from pydantic import Json

from odoo import _, api, fields
from odoo.exceptions import AccessDenied

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
)
from odoo.addons.fs_file.fields import FSFileValue

from ..dependencies import state_code_to_state_id
from ..schemas import (
    ClassifiedAdsCreate,
    ClassifiedAdsList,
    ClassifiedAdsSearchParams,
    ClassifiedAdsUpdate,
    State,
)

classified_ads_router = APIRouter(tags=["classified_ads"])


@classified_ads_router.post("/classified_ads/", status_code=201)
def create(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[Partner, Depends(authenticated_partner)],
    code_to_state_id: Annotated[dict[str, int], Depends(state_code_to_state_id)],
    parameters: Annotated[Json[ClassifiedAdsCreate], Form()],
    file: UploadFile = None,
) -> ClassifiedAdsList:
    """Create a new draft ad, waiting for submission."""
    data = parameters.to_alc_classified_create_vals(code_to_state_id)
    data["partner_id"] = partner.id
    if file:
        # create a IO from file like object
        f_name = env["alc.classified"]._get_filename(data["name"])
        data["file"] = FSFileValue(name=f"{f_name}.pdf", value=file.file.read())
    classified = env["alc.classified"].sudo().create(data)
    return ClassifiedAdsList.from_alc_classified(classified, private=True)


@classified_ads_router.get(
    "/classified_ads/search", status_code=200, response_model_exclude_unset=True
)
def search(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[Partner, Depends(authenticated_partner)],
    code_to_state_id: Annotated[dict[str, int], Depends(state_code_to_state_id)],
    params: Annotated[ClassifiedAdsSearchParams, Depends()],
    page: int | None = 1,
    per_page: int | None = 10,
) -> ClassifiedAdsList:
    """Search published classified ads.

    Does not allow to filter on state.
    """
    domain = _get_domain(
        private=False,
        parameters=params,
        partner=partner,
        state_code_to_state=code_to_state_id,
    )
    total_count, records = _paginate_search(env, domain, page=page, per_page=per_page)
    result = ClassifiedAdsList.from_alc_classified(records, private=True)
    result.size = total_count
    return result


@classified_ads_router.get("/classified_ads/my_classified_ads", status_code=200)
def my_classified_ads(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[Partner, Depends(authenticated_partner)],
    code_to_state_id: Annotated[dict[str, int], Depends(state_code_to_state_id)],
    params: Annotated[ClassifiedAdsSearchParams, Depends()],
    state: State | None = None,
    page: int | None = 1,
    per_page: int | None = 10,
) -> ClassifiedAdsList:
    """Search my classified ads.

    Allows to filter on state.
    """
    domain = _get_domain(
        private=True,
        parameters=params,
        partner=partner,
        state_code_to_state=code_to_state_id,
    )
    if state:
        domain.append(("state", "=", state.value))
    total_count, records = _paginate_search(env, domain, page=page, per_page=per_page)
    result = ClassifiedAdsList.from_alc_classified(records, private=False)
    result.size = total_count
    return result


@classified_ads_router.delete("/classified_ads/{_id}", status_code=204)
def delete(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[Partner, Depends(authenticated_partner)],
    _id: int,
) -> None:
    """Delete an ad."""
    classified = env["alc.classified"].browse(_id)
    _check_private_classified_access(classified, partner)
    classified.unlink()


@classified_ads_router.post("/classified_ads/{_id}/submit", status_code=202)
def submit(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[Partner, Depends(authenticated_partner)],
    _id: int,
) -> None:
    """Submit an ad for publication."""
    classified = env["alc.classified"].browse(_id)
    _check_private_classified_access(classified, partner)
    classified.submit()


@classified_ads_router.post("/classified_ads/{_id}/update_set_to_draft")
def update_set_to_draft(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[Partner, Depends(authenticated_partner)],
    code_to_state_id: Annotated[dict[str, int], Depends(state_code_to_state_id)],
    _id: int,
    parameters: Annotated[Json[ClassifiedAdsUpdate], Form()] = None,
    file: UploadFile = None,
) -> ClassifiedAdsList:
    """Update any field and then unpublishes the ad."""
    classified = env["alc.classified"].browse(_id)
    _check_private_classified_access(classified, partner)
    data = {}
    if parameters:
        data = parameters.to_alc_classified_update_vals(code_to_state_id)
    if file:
        f_name = env["alc.classified"]._get_filename(data.get("name", classified.name))
        data["file"] = FSFileValue(name=f"{f_name}.pdf", value=file.file.read())
    classified.update_set_to_draft(data)
    return ClassifiedAdsList.from_alc_classified(classified, private=True)


@classified_ads_router.post("/classified_ads/{_id}/update_set_to_pending")
def update_set_to_pending(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[Partner, Depends(authenticated_partner)],
    code_to_state_id: Annotated[dict[str, int], Depends(state_code_to_state_id)],
    _id: int,
    parameters: Annotated[Json[ClassifiedAdsUpdate], Form()] = None,
    file: UploadFile = None,
) -> ClassifiedAdsList:
    """Update any field.

    It unpublishes the ad and directly resubmit it.
    """
    classified = env["alc.classified"].browse(_id)
    _check_private_classified_access(classified, partner)
    data = {}
    if parameters:
        data = parameters.to_alc_classified_update_vals(code_to_state_id)
    if file:
        f_name = env["alc.classified"]._get_filename(data.get("name", classified.name))
        data["file"] = FSFileValue(name=f"{f_name}.pdf", value=file.file.read())
    classified.update_set_to_pending(data)
    return ClassifiedAdsList.from_alc_classified(classified, private=True)


@classified_ads_router.get(
    "/classified_ads/{_id}", status_code=200, response_model_exclude_unset=True
)
def get(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[Partner, Depends(authenticated_partner)],
    _id: int,
) -> ClassifiedAdsList:
    """Returns all private fields iff it belongs to the partner,.

    otherwise return all published fields. If the ad is not published or not
    accessible, access is denied.
    """
    classified = env["alc.classified"].browse(_id)
    _check_private_classified_access(classified, partner)
    private = classified.partner_id == partner
    return ClassifiedAdsList.from_alc_classified(classified, private=private)


def _paginate_search(env, domain, page=1, per_page=10):
    total_count = env["alc.classified"].search_count(domain)
    offset = per_page * (page - 1)
    records = env["alc.classified"].search(domain, limit=per_page, offset=offset)
    return total_count, records


def _get_domain(
    private: bool,
    parameters: ClassifiedAdsUpdate,
    partner: Partner,
    state_code_to_state: dict[str, id],
):
    params = parameters.model_dump(exclude_unset=True)
    params.pop("state", None)  # only acceptable in private!
    if private:
        domain = [("partner_id", "=", partner.id)]
    else:
        today = fields.Date.today()
        domain = [
            ("state", "=", "published"),
            ("date_start", "<=", today),
            ("date_end", ">=", today),
        ]
    from_date = params.pop("from_date", None)
    if from_date:
        domain.append(("date_start", ">=", from_date))
    state_code = params.pop("country_state_code", None)
    if state_code:
        domain.append(("state_id", "=", state_code_to_state[state_code.value]))
    category = params.pop("category", None)
    if category:
        domain.append(("category", "=", category.value))
    for param in ("name", "body", "phone", "contact"):
        if params.get(param):
            value = params.pop(param)
            domain.append((param, "ilike", f"%%{value}%%"))
    return domain


def _check_private_classified_access(classified, partner):
    if not classified.partner_id == partner:
        unpublished = classified.state != "published"
        if unpublished or classified.is_past or classified.is_future:
            raise AccessDenied(_("This classified ad cannot be retrieved."))
