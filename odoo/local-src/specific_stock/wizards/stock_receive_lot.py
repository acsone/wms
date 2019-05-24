# -*- coding: utf-8 -*-
# © 2017 Jacques-Etienne Baudoux (BCIM)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockPackOperationLotAdd(models.TransientModel):
    _inherit = 'stock.pack.operation.lot.add'

    qty_backorder = fields.Integer(
        'Backorder',
        compute='_get_qty_backorder',
        help="Missing quantity of products to pick",
    )

    @api.depends('operation_id')
    @api.one
    def _get_qty_backorder(self):
        """
        Set the quantity back-order. If the quantity available on a product
        is less than zero it means that there are some back-orders with this
        product.
        :return:
        """
        qty_available = self.operation_id.product_id.immediately_usable_qty

        if qty_available >= 0:
            self.qty_backorder = 0
        else:
            # Take the inverse of quantity available. If the quantity available
            # is equal to -5, it means that 5 unit of this product
            # must be keep for BO.
            self.qty_backorder = qty_available * -1

    @api.onchange('operation_id')
    def _onchange_operation_id(self):
        super(StockPackOperationLotAdd, self)._onchange_operation_id()
        if self.qty_backorder:
            if self.operation_id.location_dest_id.usage == 'internal':
                self.location_dest_id = self.operation_id.location_dest_id
            else:
                self.location_dest_id = False
