# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockQuantPackage(models.Model):

    _inherit = "stock.quant.package"

    picking_id = fields.Many2one("stock.picking", "Picking")
