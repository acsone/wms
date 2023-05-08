# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.stock.models.stock_move_line import StockMoveLine as StockMoveLineBase


class StockMoveLine(StockMoveLineBase):

    has_missing_info = fields.Boolean(
        default=False, compute="_compute_has_missing_info"
    )

    @api.depends(
        "product_id",
        "product_id.has_no_dimensions",
        "product_id.packaging_has_no_dimensions",
        "product_id.missing_weight",
        "product_id.missing_barcode",
        "product_id.is_new",
    )
    def _compute_has_missing_info(self):
        """
        We are only interested in flagging the missing infos for "new" products.

        Missing info will be either missing dimensions, packaging dimensions, weight or barcode
        """
        for move_line in self:
            product = move_line.product_id
            if product.is_new:
                move_line.has_missing_info = (
                    product.has_no_dimensions
                    or product.packaging_has_no_dimensions
                    or product.missing_weight
                    or product.missing_barcode
                )
            else:
                move_line.has_missing_info = False
