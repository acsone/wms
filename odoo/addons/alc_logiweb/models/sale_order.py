# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

CARRIER_XML_ID_BY_B2C_KEY = {
    "GLS_BE": "alc_delivery_carrier_gls.delivery_carrier_gls_be",
    "GLS_FR": "alc_delivery_carrier_gls.delivery_carrier_gls_fr",
}


class SaleOrder(models.Model):

    _inherit = "sale.order"

    sale_channel = fields.Selection(selection_add=[("logiweb", "Logiweb")])

    @api.model
    def _parse_b2c_order(self, data, b2c_backend):
        order_data = super(SaleOrder, self)._parse_b2c_order(data, b2c_backend)
        if b2c_backend.sale_channel != "logiweb":
            return order_data
        carrier = data.get("carrier")
        if not carrier:
            raise ValidationError(_("Missing carrier"))
        order_data["carrier_id"] = self.env.ref(CARRIER_XML_ID_BY_B2C_KEY[carrier]).id
        # the shipping address must be the final customer
        order_data["partner_shipping_id"] = order_data["partner_id"]
        return order_data
