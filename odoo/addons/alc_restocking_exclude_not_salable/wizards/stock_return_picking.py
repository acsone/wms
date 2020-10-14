# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockReturnPicking(models.TransientModel):

    _inherit = "stock.return.picking"

    has_archived_product = fields.Boolean(default=False)
    archived_products_message = fields.Html(readonly=True)
    has_not_salable_product = fields.Boolean(default=False)

    @api.model
    def default_get(self, fields):

        products_archived = []
        res = super(StockReturnPicking, self).default_get(fields)
        moves = []
        for move in res.get("product_return_moves", []):
            product = self.env["product.product"].browse(move[2].get("product_id"))
            move[2]["not_salable_product"] = not product.sale_ok
            res["has_not_salable_product"] = True
            if not product.active:
                res["has_archived_product"] = True
                products_archived.append(product)
            else:
                moves.append(move)
        res["product_return_moves"] = moves
        res["archived_products_message"] = self.env.ref(
            "alc_restocking_exclude_not_salable.archived_products_message"
        ).render({"products_archived": products_archived})
        return res
