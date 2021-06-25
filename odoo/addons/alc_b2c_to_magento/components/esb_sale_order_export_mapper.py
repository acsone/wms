# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class EsbSaleExportMapper(Component):
    _inherit = "esb.sale.order.export.mapper"

    @mapping
    def compute_customer_esbref(self, record):
        if record.b2c_ref:
            return {"customer_id": self.env.ref("alc_b2c_partner.b2c_customer").ref}
        return super(EsbSaleExportMapper, self).compute_customer_esbref(record)

    @mapping
    def compute_channel(self, record):
        if record.b2c_ref:
            return {"channel": "01"}
        return super(EsbSaleExportMapper, self).compute_channel(record)
