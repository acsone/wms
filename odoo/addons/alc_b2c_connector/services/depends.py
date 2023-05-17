# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from fastapi import Depends

from odoo.api import Environment

from odoo.addons.fastapi.depends import authenticated_partner_env

from ..models.fastapi_endpoint import __fastapi_endpoint_settings_base
from ..models.fastapi_endpoint_settings import FastapiEndpointSettings


def fastapi_endpoint_settings(
    settings: FastapiEndpointSettings = Depends(
        __fastapi_endpoint_settings_base
    ),  # noqa: B008
    env: Environment = Depends(authenticated_partner_env),
) -> FastapiEndpointSettings:
    return env[settings._name].browse(settings.id)
