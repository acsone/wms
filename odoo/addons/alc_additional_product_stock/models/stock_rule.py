# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.stock.models.stock_rule import StockRule as StockRuleBase


class StockRule(StockRuleBase):
    def _get_custom_move_fields(self):
        return [
            *super()._get_custom_move_fields(),
            "main_move_id",
            "is_additional_move",
        ]

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
        move_dest = values.get("move_dest_ids")
        if move_dest:
            stock_move_values["is_additional_move"] = move_dest[0].is_additional_move
        return stock_move_values

    def _push_prepare_move_copy_values(self, move_to_copy, new_date):
        values = super()._push_prepare_move_copy_values(move_to_copy, new_date)
        values["is_additional_move"] = move_to_copy.is_additional_move
        return values
