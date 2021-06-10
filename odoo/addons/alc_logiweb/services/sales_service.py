# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component

SCHEMA_CARRIER = {"type": "string", "nullable": True, "required": False}
SCHEMA_GLS_PARCEL_SHOP = {"type": "string", "required": False, "nullable": True}


class SalesService(Component):

    _inherit = "sales.service"

    def _validator_create(self):
        res = super(SalesService, self)._validator_create()
        carriers = SCHEMA_CARRIER.copy()
        carriers["allowed"] = self.env["sale.order"]._b2c_carriers().keys()
        res["carrier"] = carriers
        res["gls_parcel_shop"] = SCHEMA_GLS_PARCEL_SHOP
        return res

    def _sale_order_to_search_result(self, sale_order):
        res = super(SalesService, self)._sale_order_to_search_result(sale_order)
        res["carrier"] = sale_order._carriers_to_b2c(sale_order.carrier_id)
        res["gls_parcel_shop"] = sale_order.gls_parcel_shop or None
        return res

    @property
    def _sale_info_schema(self):
        res = super(SalesService, self)._sale_info_schema
        res["carrier"] = SCHEMA_CARRIER
        res["gls_parcel_shop"] = SCHEMA_GLS_PARCEL_SHOP
        return res
