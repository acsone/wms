# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.base.models.res_users import Users
from odoo.addons.stock.models.stock_picking import Picking


class StockPicking(Picking):

    user_id = fields.Many2one[Users](
        domain=lambda self: [
            "|",
            ("groups_id", "in", self.env.ref("stock.group_stock_user").id),
            ("share", "=", True),
        ],
    )
