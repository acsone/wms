# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.alc_b2c_partner.models.res_partner import ResPartner as ResPartnerBase


class ResPartner(ResPartnerBase):
    in_geo_release_channel = fields.Boolean(
        compute="_compute_in_geo_release_channel", store=True, readonly=False
    )

    @api.depends("is_b2c_customer")
    def _compute_in_geo_release_channel(self):
        self.filtered("is_b2c_customer").update({"in_geo_release_channel": False})
