# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    release_channel_process_end_time_delay = fields.Integer(
        related="company_id.release_channel_process_end_time_delay", readonly=False
    )
