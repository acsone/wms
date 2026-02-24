from odoo.addons.component.core import Component


class StockAction(Component):
    """Provide methods to work with stock operations."""

    _inherit = "shopfloor.stock.action"

    def unmark_move_line_as_picked(self, move_lines):
        res = super().unmark_move_line_as_picked(move_lines)
        move_lines.write({"lot_id": False})
        return res
