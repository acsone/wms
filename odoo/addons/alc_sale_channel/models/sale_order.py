# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.sale_channel.models.sale_order import SaleOrder as SaleOrderBase


class SaleOrder(SaleOrderBase):
    sale_channel_id = fields.Many2one(
        compute="_compute_sale_channel_id", store=True, readonly=False
    )

    @api.depends("team_id")
    def _compute_sale_channel_id(self):
        for rec in self:
            if not rec.sale_channel_id:
                rec.sale_channel_id = rec.team_id.sale_channel_id
