# -*- coding: utf-8 -*-
# Copyright 2016 Vincent Renaville (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class StockReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    @api.multi
    def _create_returns(self):
        # we want to do unpack for returns
        quant_obj = self.env["stock.quant"]
        return_moves = self.product_return_moves.mapped("move_id")
        for move in return_moves:
            # search associate quants
            quants = quant_obj.search(
                [
                    ("history_ids", "in", move.id),
                    ("package_id", "!=", False),
                    ("location_id", "child_of", move.location_dest_id.id),
                ]
            )
            for quant in quants:
                quant.package_id.unpack()
        return super(StockReturnPicking, self)._create_returns()

    @api.model
    def default_get(self, _fields):
        result = super(StockReturnPicking, self).default_get(_fields)
        if not result.get("product_return_moves"):
            return result
        # first get all the display_name values to have 1 sql query rather than
        # 1 per product
        products = self.env["product.product"].browse(
            [rel[2]["product_id"] for rel in result["product_return_moves"]]
        )
        names = {product.id: product.display_name for product in products}

        for __, __, line_vals in result["product_return_moves"]:
            line_vals["product_name"] = names[line_vals["product_id"]]
            line_vals["to_refund_so"] = True
        return result


class StockReturnPickingLine(models.TransientModel):
    _inherit = "stock.return.picking.line"
    _rec_name = "product_name"

    product_name = fields.Char(string="Product", readonly=True)
