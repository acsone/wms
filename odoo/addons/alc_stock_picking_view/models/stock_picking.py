# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _

from odoo.addons.stock.models.stock_picking import Picking


class StockPicking(Picking):
    def action_view_all_move(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Moves"),
            "res_model": self.move_ids._name,
            "domain": [("picking_id", "=", self.id)],
            "view_mode": "tree,form",
            "context": self.env.context,
        }

    def action_view_all_move_line(self):
        return {
            "type": "ir.actions.act_window",
            "name": _("Move Lines"),
            "res_model": self.move_line_ids._name,
            "domain": [("picking_id", "=", self.id)],
            "view_mode": "tree,form",
            "context": self.env.context,
        }

    def action_view_related_picking(self):
        pickings = (
            self.move_ids.move_dest_ids | self.move_ids.move_orig_ids
        ).picking_id
        return {
            "type": "ir.actions.act_window",
            "name": _("Related Pickings"),
            "res_model": self._name,
            "domain": [("id", "in", pickings.ids)],
            "view_mode": "tree,form",
            "context": {**self.env.context, "search_default_available": False},
        }
