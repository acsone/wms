# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from fastapi import Depends

from odoo.api import Environment

from odoo.addons.fastapi.dependencies import authenticated_partner_env

from ..models.alc_b2c_client import AlcB2cClient
from ..models.fastapi_endpoint import __alc_b2c_client_base


def alc_b2c_client(
    client: AlcB2cClient = Depends(__alc_b2c_client_base),  # noqa: B008
    env: Environment = Depends(authenticated_partner_env),  # noqa: B008
) -> AlcB2cClient:
    return env[client._name].browse(client.id)
