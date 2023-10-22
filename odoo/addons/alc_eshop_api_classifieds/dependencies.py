# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from typing import Annotated

from fastapi import Depends

from odoo.api import Environment

from odoo.addons.fastapi.dependencies import odoo_env


def state_code_to_state_id(
    env: Annotated[Environment, Depends(odoo_env)]
) -> dict[str, int]:
    """Return a mapping of state code to state id for states in Belgium."""
    return env["res.country.state"].sudo()._get_belgium_state_id_by_code()
