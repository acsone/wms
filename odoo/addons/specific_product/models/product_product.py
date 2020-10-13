# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"
    _order = "default_code"

    def action_open_incoming_stock_moves(self):
        return self.product_tmpl_id.action_open_incoming_stock_moves()

    count_pickings_to_do = fields.Integer(
        string="Incoming Pickings", compute="_compute_incoming_pickings"
    )

    def _compute_incoming_pickings(self):
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
            rec.count_pickings_to_do = pinking_count_by_product[rec.id]
