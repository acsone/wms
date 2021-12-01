# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPickingType(models.Model):

    _inherit = "stock.picking.type"

    empty_internal_package_on_transfer = fields.Boolean(
        help="If set internal packages are emptied after the transfer or "
        "when products are put in pack.",
        default=True,
    )
