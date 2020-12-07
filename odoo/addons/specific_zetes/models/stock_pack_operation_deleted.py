# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPackOperationDeleted(models.Model):

    _name = "stock.pack.operation.deleted"
    _description = "Deleted Stock Pack Operation "

    deleted_id = fields.Integer(
        "The identifier of the deleted pack operation", index=True, required=True
    )
    picking_id = fields.Many2one(
        "stock.picking",
        "Stock Picking",
        required=True,
        help="The stock operation where the delted packing has been made",
    )
    product_id = fields.Many2one("product.product", "Product", ondelete="cascade")

    @api.model
    def autovacuum(self):
        """
        Delete all records older than 2 months
        """
        self.env.cr.execute(
            """
            DELETE FROM stock_pack_operation_deleted
            WHERE create_date < now()-'2 month'::interval;
            """
        )
