# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.stock.models.stock_rule import StockRule as RuleBase


class StockRule(RuleBase):

    def _get_stock_move_values(
        self,
        product_id,
        product_qty,
        product_uom,
        location_dest_id,
        name,
        origin,
        company_id,
        values,
    ):
        stock_move_values = super()._get_stock_move_values(
            product_id,
            product_qty,
            product_uom,
            location_dest_id,
            name,
            origin,
            company_id,
            values,
        )
        # Don't set the require other lines property on moves if rule's route is MTO
        if (
            "delivery_requires_other_lines" in stock_move_values
            and self.route_id.is_mto
        ):
            stock_move_values["delivery_requires_other_lines"] = False
        return stock_move_values
