# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShopfloorMenu(models.Model):

    _inherit = "shopfloor.menu"

    delivery_carrier_ids = fields.Many2many(
        comodel_name="delivery.carrier",
        string="Delivery Methods allowed for the cluster",
        help="List of eligible device methods when creating a batch transfer",
    )
