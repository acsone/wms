# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):

    _inherit = "sale.order"

    sale_channel = fields.Selection(selection_add=[("logiweb", "Logiweb")])

    @api.model
    def _b2c_carriers(self):
        return {
            "GLS_BE": "alc_delivery_carrier_gls.delivery_carrier_gls_be",
            "GLS_FR": "alc_delivery_carrier_gls.delivery_carrier_gls_fr",
        }

    @api.model
    def _carriers_to_b2c(self, carrier):
        carriers = self._b2c_carriers()
        carrier_xmlids = carrier.get_xml_id().values()
        carrier_keys = [k for k in carriers if carriers[k] in carrier_xmlids]
        return carrier_keys[0] if carrier_keys else carrier.name if carrier else None

    @api.model
    def _parse_b2c_order(self, data, b2c_backend):
        order_data = super(SaleOrder, self)._parse_b2c_order(data, b2c_backend)
        if b2c_backend.sale_channel != "logiweb":
            return order_data
        carrier = data.get("carrier")
        if not carrier:
            raise ValidationError(_("Missing carrier"))
        order_data["carrier_id"] = self.env.ref(self._b2c_carriers()[carrier]).id
        if data.get("gls_parcel_shop"):
            order_data["gls_parcel_shop"] = data["gls_parcel_shop"]
        # the shipping address must be the final customer
        order_data["partner_shipping_id"] = order_data["partner_id"]
        return order_data
