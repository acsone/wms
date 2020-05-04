# -*- coding: utf-8 -*-
# 2019 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class ProcurementOrder(models.Model):
    _inherit = "procurement.order"

    def _get_orderpoint_domain(self, company_id=False):
        """bypass the normal domain if a list of orderpoint is available in the context"""
        orderpoint_ids = self.env.context.get("orderpoint_ids")
        if orderpoint_ids is not None:
            return [("id", "in", tuple(orderpoint_ids))]
        else:
            return super(ProcurementOrder, self)._get_orderpoint_domain(
                company_id=company_id
            )
