# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.connector_search_engine.models.se_backend import (
    SeBackend as SeBackendBase,
)


class SeBackend(SeBackendBase):

    # The queue capacity must be set to 1 since OpensSearch doesn't support
    # concurrent update of roles
    def create_or_update_linked_role(self, record):
        values = record._get_vals()
        domain = record._get_linked_roles_domain()
        existing_role = self.env["elasticsearch.role"].search(domain)
        if not existing_role:
            values["backend_id"] = self.id
            values[record._get_inverse_field_name()] = record.id
            existing_role.create(values)
        else:  # by construction, we should get at most one
            existing_role.write(values)
