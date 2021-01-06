# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPackOperationLot(models.Model):

    _inherit = "stock.pack.operation.lot"

    is_product_expired = fields.Boolean(related="lot_id.is_expired", readonly=True)
