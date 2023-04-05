# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.purchase.models.purchase import (
    PurchaseOrderLine as PurchaseOrderLineBase,
)


class PurchaseOrderLine(PurchaseOrderLineBase):
    is_bo_line = fields.Boolean("BO Line", compute="_compute_is_bo_line")

    @api.depends("product_id")
    def _compute_is_bo_line(self):
        """
        Compute if the PO line is contains a product in BO.

        :return:
        """
        for rec in self:
            rec.is_bo_line = rec.product_id.immediately_usable_qty < 0
