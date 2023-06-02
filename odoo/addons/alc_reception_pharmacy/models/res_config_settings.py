# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.base.models.res_config import ResConfigSettings as ConfigSettings


class ResConfigSettings(ConfigSettings):

    delivered_by_alcyon_constraint = fields.Boolean(
        related="company_id.delivered_by_alcyon_constraint",
        readonly=False,
    )
