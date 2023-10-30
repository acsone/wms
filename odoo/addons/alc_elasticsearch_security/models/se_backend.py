# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.connector_search_engine.models.se_backend import (
    SeBackend as SeBackendBase,
)


class SeBackendElasticsearch(SeBackendBase):
    def create_pricelist_roles(self):
        self.ensure_one()
        pricelists = self.env["product.pricelist"].search([])
        for pricelist in pricelists:
            self.create_or_update_linked_role(pricelist)
