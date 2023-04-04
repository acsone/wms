# © 2017 Jacques-Etienne Baudoux (BCIM)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields

from odoo.addons.alc_stock_receive_lot.wizards.stock_pack_operation_lot_add import (
    StockPackOperationLotAdd as LotAddBase,
)


class StockPackOperationLotAdd(LotAddBase):

    qty_backorder = fields.Integer(
        "Backorder",
        compute="_compute_qty_backorder",
        help="Missing quantity of products to pick",
    )

    @api.depends("move_line_id")
    def _compute_qty_backorder(self) -> None:
        """
        Set the quantity back-order.

        If the quantity available on a product
        is less than zero it means that there are some back-orders with this
        product.
        :return:
        """
        for rec in self:
            qty_available = rec.move_line_id.product_id.immediately_usable_qty

            if qty_available >= 0:
                rec.qty_backorder = 0
            else:
                # Take the inverse of quantity available. If the quantity available
                # is equal to -5, it means that 5 unit of this product
                # must be kept for BO.
                rec.qty_backorder = qty_available * -1
