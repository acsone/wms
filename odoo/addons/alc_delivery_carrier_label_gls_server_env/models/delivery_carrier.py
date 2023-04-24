# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import threading

from odoo import api, fields

from odoo.addons.delivery.models import delivery_carrier
from odoo.addons.server_environment.models import server_env_mixin


class DeliveryCarrier(
    delivery_carrier.DeliveryCarrier, server_env_mixin.ServerEnvMixin
):
    _name = "delivery.carrier"
    _server_env_section_name_field = "env_section_name"

    _sql_constraints = [  # we cannot really put the constraint on the name...
        ("name_uniq", "unique(product_id)", "Carrier name must be unique."),
    ]

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
            "gls_contact_id",
            "gls_url",
            "gls_url_test",
            "gls_url_tracking",
            "prod_environment",
        ]
        res = super()._server_env_fields
        if not (
            getattr(threading.current_thread(), "testing", False)
            or self.env.registry.in_test_mode()
        ):
            res.update({k: {} for k in _gls_env_fields})
        return res
