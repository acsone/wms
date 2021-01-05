# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ProductChangeQuantity(models.TransientModel):
    _inherit = "stock.change.product.qty"

    # Extend the field to change the domain.
    # An override of StockQuant.quant_move() prevents to add a quant
    # in an 'act_as_view' location anyway, but this is for UX.
    location_id = fields.Many2one(
        domain="[('usage', '=', 'internal'), ('act_as_view', '=', False)]"
    )
