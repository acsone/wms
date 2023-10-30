# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from typing import Annotated

from fastapi import APIRouter, Depends

from odoo import api

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.fastapi.dependencies import (
    authenticated_partner,
    authenticated_partner_env,
)

from ..schemas import VeterinaryGroup, VeterinaryGroupList

veterinary_groups_router = APIRouter(tags=["veterinary_groups"])


@veterinary_groups_router.get("/veterinary_groups")
def get(
    env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    partner: Annotated[Partner, Depends(authenticated_partner)],
) -> VeterinaryGroupList:
    """Retrieve informations of veterinary groups for the current partner."""
    domain = [("id", "in", partner.sudo().veterinary_group_ids.ids)]
    groups = env["veterinary.group"].sudo().search(domain)
    return VeterinaryGroupList(
        size=len(groups),
        data=[
            VeterinaryGroup(
                id=g.id,
                name=g.name,
                color=g.display_color or None,
                is_alcyonnaire=g.is_alcyonnaire,
                sequence=g.sequence,
            )
            for g in groups
        ],
    )
