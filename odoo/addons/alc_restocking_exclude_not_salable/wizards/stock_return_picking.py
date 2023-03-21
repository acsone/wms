# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.stock.wizard.stock_picking_return import ReturnPicking


class StockReturnPicking(ReturnPicking):

    has_archived_product = fields.Boolean(default=False)
    archived_products_message = fields.Html(readonly=True)
    has_not_salable_product = fields.Boolean(default=False)

    @api.onchange("picking_id")
    def _onchange_picking_id(self):
        # override odoo
        res = super()._onchange_picking_id()
        inactive_product_moves = self.env["stock.return.picking.line"]
        for move in self.product_return_moves:
            product = move.product_id
            move.not_salable_product = not product.sale_ok
            self.has_not_salable_product = (
                self.has_not_salable_product or move.not_salable_product
            )
            if not product.active:
                self.has_archived_product = True
                inactive_product_moves |= move
        self.product_return_moves -= inactive_product_moves
        self.archived_products_message = self.env["ir.ui.view"]._render_template(
            "alc_restocking_exclude_not_salable.archived_products_message",
            {"inactive_product_moves": inactive_product_moves},
        )
        return res
