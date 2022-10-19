# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    delivery_resource_id = fields.Many2one(
        comodel_name="alc.delivery.resource", string="Image", ondelete="set null",
    )
