# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import ormcache

MAIL_KEY = "sale_mail_internal.send_email"


class SaleConfigSettings(models.TransientModel):

    _inherit = "sale.config.settings"

    send_confirmation_email_internal = fields.Boolean(
        "Send an email when confirming internal orders.", default=False
    )

    @api.model
    @ormcache()
    def get_send_confirmation_email_internal(self):
        IrConfigParameter = self.env["ir.config_parameter"].sudo()
        return bool(IrConfigParameter.get_param(MAIL_KEY, ""))

    @api.model
    def default_get(self, _fields):
        res = super(SaleConfigSettings, self).default_get(_fields)
        if "send_confirmation_email_internal" in _fields or not _fields:
            send = self.get_send_confirmation_email_internal()
            res["send_confirmation_email_internal"] = send
        return res

    def set_send_confirmation_email_internal(self):
        self.ensure_one()
        value = "1" if self.send_confirmation_email_internal else ""
        self.env["ir.config_parameter"].sudo().set_param(MAIL_KEY, value)
