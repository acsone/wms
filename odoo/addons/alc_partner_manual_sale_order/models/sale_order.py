# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    manual_sale_order_allowed = fields.Boolean(
        related="partner_id.manual_sale_order_allowed"
    )
