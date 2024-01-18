# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api

from odoo.addons.connector_search_engine.models.se_backend import (
    SeBackend as SeBackendBase,
)


class SeBackend(SeBackendBase):
    def button_synchronize_ads(self):
        self.ensure_one()
        ads_model = self.env["alc.eshop.ads"]
        ads_model.search([("is_published", "=", True)]).action_synchronize_ads()

    @api.model
    def cron_synchronize_ads(self):
        for backend in self.search([]):
            backend.button_synchronize_ads()
