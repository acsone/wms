# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from slugify import slugify

from odoo import _, api, models


class ElasticsearchRoleMixin(models.AbstractModel):

    _name = "elasticsearch.role.mixin"
    _description = "elasticsearch role mixin"

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records.delay_create_or_update_linked_role()
        return records

    @api.model
    def _get_inverse_field_name(self):
        """Default inverse field; override (without super) if different."""
        return self._name.rsplit(".", maxsplit=1)[-1] + "_id"

    def _get_linked_roles_domain(self):
        return [(self._get_inverse_field_name(), "in", self.ids)]

    def unlink(self):
        domain_roles = self._get_linked_roles_domain()
        roles = self.env["elasticsearch.role"].search(domain_roles)
        roles.unlink()
        return super().unlink()

    @api.model
    def _get_role_name_fields(self):
        """Default role name fields; override (without super) if different."""
        # note this method is coupled to _get_role_name; only these fields should be
        # used to compute the role name
        return "name"

    def _get_role_name(self):
        """Default role name; override (without super) if different."""
        # note this method is coupled to _get_role_name_fields; it should depend
        # only on these fields
        self.ensure_one()
        return slugify(self.name)

    def delay_create_or_update_linked_role(self):
        if self.env.context.get("ignore_es_update_role"):
            return
        backends = self.env["se.backend"].search([])
        for bkd in backends:
            for record in self:
                name = record._get_role_name()
                desc = _("Create Role on ElasticSearch: %(name)s", name=name)
                bkd.with_delay(description=desc).create_or_update_linked_role(record)

    def write(self, vals):
        if any(field in vals for field in self._get_role_name_fields()):
            self.delay_create_or_update_linked_role()
        return super().write(vals)

    def _get_role_body(self):
        """Main method.

        No default implementation.
        """
        self.ensure_one()
        raise NotImplementedError

    def _get_vals(self):
        self.ensure_one()
        return {"body": self._get_role_body(), "name": self._get_role_name()}
