# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.purchase.models.purchase import PurchaseOrder as PurchaseOrderBase


class PurchaseOrder(PurchaseOrderBase):

    total_weight = fields.Float(
        "Total weight",
        compute="_compute_total_weight",
        readonly=True,
        help="Total weight",
    )
    weight_uom_name = fields.Char(
        string="Weight unit of measure label", compute="_compute_weight_uom_name"
    )

    def _compute_weight_uom_name(self):
        self.update(
            {
                "weight_uom_name": self.env[
                    "product.template"
                ]._get_weight_uom_name_from_ir_config_parameter()
            }
        )

    @api.depends("order_line")
    def _compute_total_weight(self):
        for rec in self:
            if not rec.order_line:
                rec.total_weight = 0
                continue
            rec.total_weight = sum(
                [line.product_id.weight * line.product_qty for line in rec.order_line]
            )
