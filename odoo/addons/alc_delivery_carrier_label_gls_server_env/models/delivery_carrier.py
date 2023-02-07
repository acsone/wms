# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class DeliveryCarrier(models.Model):

    _name = "delivery.carrier"
    _inherit = ["delivery.carrier", "server.env.mixin"]

    _sql_constraints = [  # we cannot really put the constraint on the name...
        ("name_uniq", "unique(product_id)", "Carrier name must be unique."),
    ]

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
        res.update({k: {} for k in _gls_env_fields})
        return res
