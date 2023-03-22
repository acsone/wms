# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import typing

from odoo import api, fields

from odoo.addons.sale_channel.models.sale_order import SaleOrder as SaleOrderBase

if typing.TYPE_CHECKING:
    pass


class SaleOrder(SaleOrderBase):
    sale_channel_id = fields.Many2one["SaleChannel"](
        compute="_compute_sale_channel_id",
        store=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )

    @api.depends("team_id")
    def _compute_sale_channel_id(self):
        for rec in self:
            if not rec.sale_channel_id:
                rec.sale_channel_id = rec.team_id.sale_channel_id
