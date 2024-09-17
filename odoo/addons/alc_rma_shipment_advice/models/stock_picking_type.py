# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.stock.models.stock_picking import PickingType


class StockPickingType(PickingType):

    is_rma = fields.Boolean(
        string="RMA Operation",
        help="Indicates if this picking type is used for RMA "
        "(Return Merchandise Authorization) operations.",
    )
