# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class CarrierAccount(models.Model):
    _name = "carrier.account"
    _inherit = ["carrier.account", "server.env.mixin"]
    _server_env_section_name_field = "env_section_name"

    env_section_name = fields.Char(
        string="Environment Section Name",
        help="Name of the section in the server environment configuration "
        "file that contains the configuration for this carrier account.",
        compute="_compute_env_section_name",
    )

    @api.depends("name")
    def _compute_env_section_name(self):
        for rec in self:
            rec.env_section_name = rec.name.replace(" ", "_")

    @property
    def _server_env_fields(self):
        _gls_env_fields = [
            "account",
            "password",
        ]
        res = super()._server_env_fields
        res.update({k: {} for k in _gls_env_fields})
        return res
