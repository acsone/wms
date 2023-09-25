# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.stock.models.stock_rule import StockRule as StockRuleBase


class StockRule(StockRuleBase):
    def _get_custom_move_fields(self):
        res = super()._get_custom_move_fields()
        res += ["product_qty_unavailable", "delivery_requires_other_lines"]
        return res
