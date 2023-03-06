# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from ast import literal_eval

from odoo import fields

from odoo.addons.stock.models.product import ProductTemplate as ProductTemplateBase


class ProductTemplate(ProductTemplateBase):

    count_incoming_moves = fields.Integer(compute="_compute_incoming_pickings")

    def _compute_incoming_pickings(self):
        for rec in self:
            rec.count_incoming_moves = sum(
                rec.mapped("product_variant_ids.count_incoming_moves")
            )

    def action_open_incoming_stock_moves(self):
        self.ensure_one()
        action = self.action_view_stock_move_lines()
        action["context"] = literal_eval(action.get("context"))
        action["context"]["search_default_todo"] = 1
        action["context"]["search_default_done"] = 0
        action["context"]["search_default_by_picking"] = 1
        action["domain"].append(("picking_type_id.code", "=", "incoming"))
        return action
