# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.purchase_stock.models import stock_rule


class StockRule(stock_rule.StockRule):
    def _make_po_get_domain(self, company_id, values, partner):
        domain = super()._make_po_get_domain(company_id, values, partner)
        # we want to pop the purchase manager from the domain to ensure
        # that the purchase manager is not used as a filter for the
        # purchase order lines
        new_domain = []
        for d in domain:
            if d[0] != "user_id":
                new_domain.append(d)
        # tansform list to tuple since domain must be hashable for the _run_buy method
        # of odoo.addons.stock.models.stock_rule.StockRule to work
        return tuple(new_domain)
