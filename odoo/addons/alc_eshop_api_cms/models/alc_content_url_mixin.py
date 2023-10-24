# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api

from odoo.addons.alc_eshop_cms import models


class AlcContentUrlMixin(models.AlcContentUrlMixin):
    @api.model
    def _get_from_url(self, url):
        _id = url.split("-")[-1]
        return self.search([("id", "=", int(_id))])
