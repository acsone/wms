# -*- coding: utf-8 -*-
# © 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class PurchaseConfigSettings(models.TransientModel):
    _inherit = "purchase.config.settings"

    lead_time = fields.Integer("Default Lead time (in days)")

    def get_default_lead_time(self, _fields):
        lead_time = int(
            self.env["ir.config_parameter"].get_param("purchase.lead_time", 0)
        )
        return {"lead_time": lead_time}

    def set_lead_time(self):
        if not self.lead_time:
            lead_time = "0"
        else:
            lead_time = str(self.lead_time)
        self.env["ir.config_parameter"].set_param("purchase.lead_time", lead_time)
