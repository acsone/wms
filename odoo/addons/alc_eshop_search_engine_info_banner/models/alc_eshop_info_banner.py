# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command

from odoo.addons.alc_eshop_info_banner.models import alc_eshop_info_banner


class AlcEshopInfoBanner(alc_eshop_info_banner.AlcEshopInfoBanner):

    def _compute_se_index(self):
        model = self.env.ref("alc_eshop_info_banner.model_alc_eshop_info_banner")
        indexes = self.env["se.index"].search([("model_id", "=", model.id)])
        self.update({"se_index_ids": [Command.set(indexes.ids)]})
