# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.stock.models.stock_rule import ProcurementGroup as ProcurementGroupBase


class ProcurementGroup(ProcurementGroupBase):
    def _get_orderpoint_domain(self, company_id=False):
        return (
            super()._get_orderpoint_domain(company_id=company_id)
            + self.env[
                "stock.warehouse.orderpoint"
            ]._filter_orderpoint_to_process_domain()
        )
