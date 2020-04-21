# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models, fields


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    # avoid_shipping_cost is used to avoid computing shipping cost for
    # outgoing picking type. It has no effect on other picking types.
    avoid_shipping_cost = fields.Boolean(
        string="Avoid shipping cost",
        default=False,
        help="Is selected, the shipping cost will not be added to the sale"
             "order.",
    )
