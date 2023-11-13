# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api

from odoo.addons.delivery.models.sale_order import SaleOrder as Order


class SaleOrder(Order):
    @api.onchange("partner_id")
    def onchange_partner_id(self):
        # alc_b2c_connector does self.sudo().play_onchanges but shouldn't play this one
        if (
            not self.env.context.get("alc_b2c_client_id")
            and self.partner_id
            and self.partner_id.property_delivery_carrier_id
        ):
            self.carrier_id = self.partner_id.property_delivery_carrier_id
