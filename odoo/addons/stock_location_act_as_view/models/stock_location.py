# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    act_as_view = fields.Boolean(
        default=False,
        help="When marked, the location will be considered as a view, "
        "meaning they must not contain stock and they have sub-locations. "
        "Usually used on internal locations, the 'view' usage should be used "
        "only on the 'view location' of the warehouses.",
    )
