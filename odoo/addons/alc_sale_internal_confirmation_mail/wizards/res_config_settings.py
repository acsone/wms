# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    send_confirmation_email_internal = fields.Boolean(
        "Send an email when confirming internal orders.",
        default=False,
        config_parameter="sale_mail_internal.send_email",
    )
