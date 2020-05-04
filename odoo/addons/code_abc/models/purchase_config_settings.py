# -*- coding: utf-8 -*-
# © 2018 Okia SPRL <Sylvain Van Hoof>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class PurchaseConfigSettings(models.TransientModel):
    _inherit = "purchase.config.settings"

    turnover_delay = fields.Integer(
        "CA computation delay (in months)",
        default=lambda self: int(
            self.env["ir.config_parameter"].get_param("abc.turnover_delay", 0)
        ),
    )

    @api.multi
    def set_turnover_delay(self):
        self.ensure_one()

        if self.turnover_delay:
            self.env["ir.config_parameter"].set_param(
                "abc.turnover_delay", self.turnover_delay
            )
