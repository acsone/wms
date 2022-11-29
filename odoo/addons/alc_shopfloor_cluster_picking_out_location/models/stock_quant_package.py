# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockQuantPackage(models.Model):

    _inherit = "stock.quant.package"
    is_scanned = fields.Boolean(
        help="Technical field to check the package has already been scanned to out location",
        default=False,
    )
