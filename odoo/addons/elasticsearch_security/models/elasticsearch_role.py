# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class ElasticSearchRole(models.Model):

    _name = "elasticsearch.role"

    name = fields.Char(required=True)
    body = fields.Text(required=True)
    backend_id = fields.Many2one(
        comodel_name="se.backend.elasticsearch",
        ondelete="cascade",
        required=True,
        readonly=True,
    )
    extra_backend_roles = fields.Char(help="Separate roles by a comma, without spaces")

    _sql_constraints = [
        (
            "name_backend_uniq",
            "unique(name, backend_id)",
            _("The name must be unique by backend!"),
        )
    ]

    def get_backend_roles(self):
        self.ensure_one()
        if self.extra_backend_roles:
            backend_roles = list(set(self.extra_backend_roles.split(",") + [self.name]))
        else:
            backend_roles = [self.name]
        return backend_roles

    def delay_synchronize(self):
        for role in self:
            desc = _("Synchronize Security Role %s") % role.name
            role.backend_id.with_delay(description=desc).synchronize_role(role)

    def synchronize(self):
        for role in self:
            role.backend_id.synchronize_role(role)

    def delay_delete_role(self, role_name):
        self.ensure_one()
        desc = _("Delete Security Role %s") % role_name
        self.backend_id.with_delay(description=desc).delete_role(role_name)

    def unlink(self):
        if not self.env.context.get("es_security_no_autosync"):
            for role in self:
                role.delay_delete_role(role.name)
        return super(ElasticSearchRole, self).unlink()

    @api.model
    def create(self, vals):
        res = super(ElasticSearchRole, self).create(vals)
        if not self.env.context.get("es_security_no_autosync"):
            res.delay_synchronize()
        return res

    def write(self, vals):
        old_names = {r.id: r.name for r in self}
        res = super(ElasticSearchRole, self).write(vals)
        if not self.env.context.get("es_security_no_autosync"):
            for role in self:
                if old_names[role.id] != role.name:
                    role.delay_delete_role(old_names[role.id])
            self.delay_synchronize()
        return res

    _sql_constraints = [
        (
            "name_backend_uniq",
            "unique (name, backend_id)",
            "Role names must be unique per backend.",
        )
    ]
