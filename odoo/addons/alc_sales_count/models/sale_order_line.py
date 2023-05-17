# Copyright 2023 ASCONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.sale.models.sale_order_line import SaleOrderLine as SaleOrderLineBase


class SaleOrderLine(SaleOrderLineBase):
    _inherit = "sale.order.line"

    # add index on the core field, used for the SQL query used in the method
    # `_compute_sales_count` in the current addon
    state = fields.Selection(index=True)
