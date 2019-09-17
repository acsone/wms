# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    # Add an index because the query in ProductProduct._get_product_last_in_date
    # benefits a lot from it (an order of magnitude)
    product_id = fields.Many2one(index=True)
