# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ElasticSearchRole(models.Model):

    _name = "elasticsearch.role"

    name = fields.Char(required=True)
    body = fields.Text(required=True)
    backend_id = fields.Many2one(
        comodel_name="se.backend.elasticsearch", ondelete="cascade", required=True
    )
    extra_backend_roles = fields.Char(help="Separate roles by a comma, without spaces")

    def get_backend_roles(self):
        self.ensure_one()
        if self.extra_backend_roles:
            backend_roles = list(set(self.extra_backend_roles.split(",") + [self.name]))
        else:
            backend_roles = [self.name]
        return backend_roles

    _sql_constraints = [
        (
            "name_backend_uniq",
            "unique (name, backend_id)",
            "Role names must be unique per backend.",
        )
    ]
