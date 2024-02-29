# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields

from odoo.addons.base.models.res_config import ResConfigSettings as ResConfigBase


class ResConfigSettings(ResConfigBase):

    restrict_move_line_quantity = fields.Boolean(
        related="company_id.restrict_move_line_quantity",
        readonly=False,
    )
