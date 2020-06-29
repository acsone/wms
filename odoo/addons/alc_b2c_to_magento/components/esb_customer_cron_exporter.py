# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.osv.expression import AND


class EsbCustomerCronExporter(Component):

    _inherit = "esb.customer.cron.exporter"

    def get_items_domain(self):
        # exclude b2c customers
        domain = super(EsbCustomerCronExporter, self).get_items_domain()
        return AND([domain, [("is_b2c_customer", "=", False)]])
