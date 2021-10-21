# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPickingWave(models.Model):

    _inherit = "stock.picking.wave"

    picking_ids = fields.One2many(auto_join=True)
