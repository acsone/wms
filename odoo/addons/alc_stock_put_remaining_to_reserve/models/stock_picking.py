# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    picking_reserve_id = fields.Many2one(
        "stock.picking",
        "Picking that goes to reserve of",
        copy=False,
        index=True,
        states={"done": [("readonly", True)], "cancel": [("readonly", True)]},
        help="If some quantities have to be put to reserve after putting some in stock, they will be placed in a new picking going to reserve",
    )
