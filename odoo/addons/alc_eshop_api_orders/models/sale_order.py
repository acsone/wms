# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.sale.models import sale_order


class SaleOrder(sale_order.SaleOrder):
    shopinvader_state = fields.Selection(
        [
            ("cancel", "Cancel"),
            ("pending", "Pending"),
            ("processing", "Processing"),
            ("shipped", "Shipped"),
        ],
        compute="_compute_shopinvader_state",
        store=True,
    )

    def _get_shopinvader_state(self):
        self.ensure_one()
        if self.state == "cancel":
            return "cancel"
        if self.state == "done":
            return "shipped"
        if self.state == "draft":
            return "pending"
        return "processing"

    def _compute_shopinvader_state_depends(self):
        return ("state",)

    @api.depends(lambda self: self._compute_shopinvader_state_depends())
    def _compute_shopinvader_state(self):
        # simple way to have more human friendly name for
        # the sale order on the website
        for record in self:
            record.shopinvader_state = record._get_shopinvader_state()
