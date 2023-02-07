# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class CarrierAccount(models.Model):
    _name = "carrier.account"
    _inherit = ["carrier.account", "server.env.mixin"]

    @property
    def _server_env_fields(self):
        _gls_env_fields = [
            "account",
            "password",
        ]
        res = super()._server_env_fields
        res.update({k: {} for k in _gls_env_fields})
        return res
