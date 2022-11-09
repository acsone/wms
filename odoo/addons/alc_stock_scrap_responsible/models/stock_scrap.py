# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.base.models.res_users import Users
from odoo.addons.stock.models.stock_scrap import StockScrap as StockScrapBase


class StockScrap(StockScrapBase):

    user_id = fields.Many2one[Users](
        string="Responsible",
        copy=False,
        tracking=True,
        compute="_compute_user_id",
        store=True,
        readonly=False,
        required=True,
        default=lambda self: self.env.user,
    )

    def _compute_user_id(self) -> None:
        for record in self:
            record.user_id = record.env.user
