# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    total_volume_batch_picking_liter = fields.Float(
        string="Volume (l)",
        help="Indicates total volume of transfers included.",
        compute="_compute_total_volume_batch_picking_liter",
    )

    @api.depends("total_volume_batch_picking")
    def _compute_total_volume_batch_picking_liter(self):
        for rec in self:
            rec.total_volume_batch_picking_liter = (
                rec.total_volume_batch_picking * 1000.0
            )

    def action_assign(self):
        """
        Hack: When we confirm a wave picking (confirm_picking method on stock_picking_wave),
        the basic mecanism assign the pickings to start the cluster. In the case of Alcyon,
        pickings are already assigned. We don't need to go through the mecanism once again.
        """
        self2 = self
        if self.env.context.get("from_cluster_confirm"):
            self2 = self.filtered(
                lambda p: p.state not in ("assigned", "partially_available")
            )
        if not self2:
            # nothing to assign
            return True
        return super(StockPicking, self2).action_assign()
