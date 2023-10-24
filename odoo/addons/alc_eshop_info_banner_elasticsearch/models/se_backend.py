# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api

from odoo.addons.connector_elasticsearch.models.se_backend import (
    SeBackend as SeBackendBase,
)


class SeBackend(SeBackendBase):
    def button_synchronize_info_banners(self):
        self.ensure_one()
        banner_model = self.env["alc.eshop.info.banner"]
        banner_model.search(
            [("is_published", "=", True)]
        ).action_synchronize_info_banners()

    @api.model
    def cron_synchronize_info_banners(self):
        self.button_synchronize_info_banners()
