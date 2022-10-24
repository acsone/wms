# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockLocation(models.Model):

    _inherit = "stock.location"
    keep_track_of_delivery_round = fields.Boolean(default=False)
    delivery_round_id = fields.Many2one(
        "round.instance",
        string="Delivery Round",
        store=True,
        readonly=False,
        index=True,
    )
