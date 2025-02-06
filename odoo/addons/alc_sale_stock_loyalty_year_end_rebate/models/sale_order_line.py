# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _compute_qty_delivered(self):
        # We override this method as a hook to compute the loyalty points
        # accrued points based on the deliverd quantity.
        res = super()._compute_qty_delivered()
        self.order_id.coupon_point_ids._refresh_accrued_points()
        return res
