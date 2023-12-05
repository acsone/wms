# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields

from odoo.addons.base.models.res_config import (
    ResConfigSettings as ResConfigSettingsBase,
)


class ResConfigSettings(ResConfigSettingsBase):

    no_user_on_backorder = fields.Boolean(
        related="company_id.no_user_on_backorder",
        readonly=False,
    )
