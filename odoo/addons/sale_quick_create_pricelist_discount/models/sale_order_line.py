# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    order_discount_pricelist_ids = fields.Many2many(
        related="order_id.discount_pricelist_ids", readonly=True
    )
