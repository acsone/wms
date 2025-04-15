# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api

from odoo.addons.connector_search_engine.models.se_backend import (
    SeBackend as SeBackendBase,
)


class SeBackend(SeBackendBase):
    def button_synchronize_loyalty_programs(self):
        self.ensure_one()
        model = self.env["loyalty.program"]
        model.search([("is_published", "=", True)]).action_synchronize_records()

    @api.model
    def cron_synchronize_loyalty_programs(self):
        backends = self or self.search([])
        for backend in backends:
            backend.button_synchronize_loyalty_programs()
