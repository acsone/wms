# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# Copyright 2021 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    total_weight = fields.Float(
        compute="_compute_picking_info",
        help="Technical field. Indicates total weight of transfers included.",
    )
    operation_count = fields.Integer(
        compute="_compute_picking_info",
        help="Technical field. Indicates number of operation included.",
    )

    @api.depends(
        "pack_operation_ids",
        "pack_operation_ids.product_qty",
        "pack_operation_ids.package_id",
    )
    def _compute_picking_info(self):
        for item in self:
            item.update(
                {
                    "total_weight": item._calc_weight(),
                    "operation_count": len(item.pack_operation_ids),
                }
            )

    def _calc_weight(self):
        weight = 0.0
        for pop in self.mapped("pack_operation_ids"):
            weight += (
                pop.product_qty
                * (pop.product_id.weight or 1)
                * (
                    pop.package_id.pack_weight
                    or pop.package_id.estimated_pack_weight
                    or 1
                )
            )
        return weight
