# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields

from odoo.addons.stock.models.stock_picking import PickingType


class StockPickingType(PickingType):

    show_serial_number = fields.Boolean(
        help="Check this if you want to allow serial numbers fill in for the"
        "corresponding pickings."
    )
