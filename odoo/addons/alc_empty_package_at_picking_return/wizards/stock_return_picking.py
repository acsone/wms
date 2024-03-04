# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.stock.wizard.stock_picking_return import ReturnPicking


class StockReturnPicking(ReturnPicking):
    def _create_returns(self):
        new_picking_id, pick_type_id = super()._create_returns()
        if self.picking_id.picking_type_id.empty_package_at_return:
            move_lines = self.env["stock.move.line"].search(
                [("picking_id", "=", new_picking_id)]
            )
            move_lines.result_package_id = False
        return new_picking_id, pick_type_id
