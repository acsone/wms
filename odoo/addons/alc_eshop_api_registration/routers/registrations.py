# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from typing import Annotated

from fastapi import APIRouter, Depends

from odoo import api

from odoo.addons.fastapi.dependencies import odoo_env

from ..schemas import RegistrationId, RegistrationRqst

registrations_router = APIRouter(tags=["registrations"])


@registrations_router.post("/registrations", status_code=202)
def create_registration(
    env: Annotated[api.Environment, Depends(odoo_env)], request: RegistrationRqst
) -> RegistrationId:
    """Submit a registration request."""
    vals = request.to_alc_registration_create(env)
    registration = env["alc.registration"].sudo().create(vals)
    return RegistrationId(id=registration.id)
