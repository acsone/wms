# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from psycopg2.extensions import AsIs

from odoo import api, fields, models


def create_index(cr, index_name, table, expression):
    cr.execute("SELECT indexname FROM pg_indexes WHERE indexname = %s", (index_name,))
    if not cr.fetchone():
        cr.execute(
            "CREATE INDEX %s " "ON %s %s",
            (AsIs(index_name), AsIs(table), AsIs(expression)),
        )


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # add index on the core field, used for the SQL query used in the method
    # `_sales_count` in the current addon
    state = fields.Selection(index=True)

    @api.model_cr
    def init(self):
        # TODO CHECK if this index is still used....
        # see https://dmitry-naumenko.medium.com/how-to-define-unused-indexes-in-postgresql-471da6f6f33f
        create_index(
            self.env.cr,
            "sale_order_line_remains_to_deliver_index",
            self._table,
            "(is_consignment, "
            "product_qty_remains_to_deliver, "
            "product_type, "
            "state)",
        )
