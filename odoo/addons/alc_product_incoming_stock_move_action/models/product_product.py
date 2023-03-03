# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.stock.models.product import Product


class ProductProduct(Product):

    count_incoming_moves = fields.Integer(
        string="Incoming Pickings", compute="_compute_count_incoming_moves"
    )

    def action_open_incoming_stock_moves(self):
        return self.product_tmpl_id.action_open_incoming_stock_moves()

    def _compute_count_incoming_moves(self):
        stock_move = self.env["stock.move"]
        domain = [
            ("product_id", "in", self.ids),
            ("picking_type_id.code", "=", "incoming"),
            ("state", "in", ("assigned", "confirmed", "waiting")),
        ]
        stock_moves_grouped_by_product_picking = stock_move.read_group(
            domain,
            fields=["product_id", "picking_id"],
            groupby=["product_id", "picking_id"],
            lazy=False,
        )
        pinking_count_by_product = {p.id: 0 for p in self}
        for item in stock_moves_grouped_by_product_picking:
            pinking_count_by_product[item["product_id"][0]] += 1
        for rec in self:
            rec.count_incoming_moves = pinking_count_by_product[rec.id]
