# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    release_channel_shipment_advice_arrival_delay = fields.Integer(
        related="company_id.release_channel_shipment_advice_arrival_delay",
        readonly=False,
    )
