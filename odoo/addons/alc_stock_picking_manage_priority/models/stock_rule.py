# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api

from odoo.addons.stock.models.stock_rule import StockRule as StockRuleBase


class StockRule(StockRuleBase):
    @api.model
    def _run_pull(self, procurements):
        """After running rules, released pickings recompute the priority."""
        return super(StockRule, self.with_context(no_check_priority=True))._run_pull(
            procurements
        )
