# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api

from odoo.addons.shopinvader_sale_cart.models import sale_order


class SaleOrder(sale_order.SaleOrder):
    @api.model
    def _prepare_cart(self, partner_id):
        vals = super()._prepare_cart(partner_id)
        vals["sale_channel_id"] = self.env.ref("alc_sale_channel.sale_channel_web").id
        vals["team_id"] = self.env.ref("sales_team.salesteam_website_sales").id
        return vals
