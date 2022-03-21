# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    @api.model
    def _get_sale_channels_internal(self):
        return [pair[0] for pair in self._get_sale_channels_internal_selection()]

    @api.model
    def _get_sale_channels_internal_selection(self):
        return [
            ("phone", "Phone"),
            ("mail", "Mail"),
            ("fax", "Fax"),
            ("web", "Web"),
        ]

    @api.model
    def _get_sale_channels_external(self):
        return [pair[0] for pair in self._get_sale_channels_external_selection()]

    @api.model
    def _get_sale_channels_external_selection(self):
        return []

    @api.model
    def _get_sale_channels_selection(self):
        internal = self._get_sale_channels_internal_selection()
        return internal + self._get_sale_channels_external_selection()

    @api.model
    def _get_sale_channels(self):
        return [pair[0] for pair in self._get_sale_channels_selection()]

    sale_channel = fields.Selection(selection="_get_sale_channels_selection")

    @api.onchange("team_id")
    def onchange_team_id(self):
        if not self.sale_channel:
            self.sale_channel = "phone"

        team_web = self.env.ref("sales_team.salesteam_website_sales")
        if self.team_id == team_web:
            self.sale_channel = "web"
