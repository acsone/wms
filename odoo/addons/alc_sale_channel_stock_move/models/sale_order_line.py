# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"
    sale_channel = fields.Selection(
        related="order_id.sale_channel", readonly=True, store=True
    )
