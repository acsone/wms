# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api

from odoo.addons.stock.models.stock_quant import StockQuant as Quant


class StockQuant(Quant):
    @api.model
    def action_view_inventory(self):
        """
        Modify default filter.

        :return: ir.actions.act_window
        """
        action = super().action_view_inventory()
        ctx = action.get("context", {})
        if "search_default_on_hand" in ctx:
            del ctx["search_default_on_hand"]
        ctx["search_default_internal_loc"] = True
        action["context"] = ctx
        return action
