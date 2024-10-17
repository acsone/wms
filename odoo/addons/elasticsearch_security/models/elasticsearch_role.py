# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.connector_elasticsearch.models.se_backend import SeBackend


class ElasticSearchRole(models.Model):

    _name = "elasticsearch.role"
    _description = "Elasticsearch Role"

    name = fields.Char(required=True)
    body = fields.Text(required=True)
    backend_id = fields.Many2one[SeBackend](
        ondelete="cascade", required=True, readonly=True
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
            backend_roles = list({*self.extra_backend_roles.split(","), self.name})
        else:
            backend_roles = [self.name]
        return backend_roles

    def unlink(self):
        if not self.env.context.get("es_security_no_autosync"):
            for role in self:
                role.delay_delete_role(role.backend_id, role.name)
        return super().unlink()

    @api.model_create_multi
    def create(self, vals):
        roles = super().create(vals)
        if self.env.context.get("es_security_no_autosync"):
            return roles
        for role in roles:
            role.delay_put_role()
        return roles

    def write(self, vals):
        old_names = {r.id: r.name for r in self}
        res = super().write(vals)
        if self.env.context.get("es_security_no_autosync"):
            return res
        for role in self:
            if old_names[role.id] != role.name:
                role.delay_delete_role(role.backend_id, old_names[role.id])
            role.delay_put_role()
        return res

    def put_role(self):
        self.ensure_one()
        try:
            security = self.backend_id._get_client_security()
            security.create_role(self.name, self.body)
            security.create_role_mapping(
                self.name, {"backend_roles": self.get_backend_roles()}
            )
        except Exception as e:
            raise ValidationError(
                _(
                    "Could not put role %(name)s.\nOriginal error:\n%(error)s",
                    name=self.name,
                    error=e,
                )
            ) from e

    def put_roles(self):
        for rec in self:
            rec.put_role()

    @api.model
    def delete_role(self, backend, name):
        self.ensure_one()
        try:
            security = backend._get_client_security()
            security.delete_role(name)
            security.delete_role_mapping(name)
        except Exception as e:
            raise ValidationError(
                _(
                    "Could not delete role %(name)s.\nOriginal error:\n%(error)s",
                    name=name,
                    error=e,
                )
            ) from e

    def delay_put_role(self):
        for role in self:
            desc = _("Synchronize Security Role %(name)s", name=role.name)
            role.with_delay(description=desc).put_role()

    def delay_delete_role(self, backend, name):
        self.ensure_one()
        desc = _("Delete Security Role %(name)s", name=self.name)
        self.with_delay(description=desc).delete_role(backend, name)
