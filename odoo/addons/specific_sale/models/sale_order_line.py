# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


def create_index(cr, index_name, table, expression):
    cr.execute("SELECT indexname FROM pg_indexes WHERE indexname = %s", (index_name,))
    if not cr.fetchone():
        cr.execute("CREATE INDEX %s " "ON %s %s" % (index_name, table, expression))


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # used for the search filter "Remains to deliver" on the order line view
    product_type = fields.Selection(
        related="product_id.type", readonly=True, store=True
    )
    is_consignment = fields.Boolean(
        related="order_id.is_consignment", readonly=True, store=True
    )
    # add index on the core field, used for the SQL query used in the method
    # `_sales_count` in the current addon
    state = fields.Selection(index=True)

    @api.model_cr
    def init(self):
        create_index(
            self.env.cr,
            "sale_order_line_remains_to_deliver_index",
            self._table,
            "(is_consignment, "
            "product_qty_remains_to_deliver, "
            "product_type, "
            "state)",
        )
