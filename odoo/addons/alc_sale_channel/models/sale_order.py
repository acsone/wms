# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    sale_channel = fields.Selection(
        [("phone", "Phone"), ("mail", "Mail"), ("fax", "Fax"), ("web", "Web")]
    )

    @api.onchange("team_id")
    def onchange_team_id(self):
        if not self.sale_channel:
            self.sale_channel = "phone"

        team_web = self.env.ref("sales_team.salesteam_website_sales")
        if self.team_id == team_web:
            self.sale_channel = "web"
