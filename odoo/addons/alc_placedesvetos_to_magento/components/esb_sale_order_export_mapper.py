# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class EsbSaleExportMapper(Component):
    _inherit = "esb.sale.order.export.mapper"

    @mapping
    def compute_customer_esbref(self, record):
        if record.sale_channel == "placedesvetos":
            return {
                "customer_id": self.env.ref(
                    "alc_placedesvetos.res_partner_placedesvetos"
                ).ref
            }
        return super(EsbSaleExportMapper, self).compute_customer_esbref(record)

    @mapping
    def compute_channel(self, record):
        # Phone channel '01' is the default
        if record.sale_channel == "placedesvetos":
            return {"channel": "01"}  # phone
        return super(EsbSaleExportMapper, self).compute_channel(record)
