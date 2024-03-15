# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.stock.models.stock_picking import PickingType


class StockPickingType(PickingType):

    show_gls_put_in_pack_wizard = fields.Boolean(
        help="If you check this and if the picking delivery carrier is GLS,"
        "the specific wizard will be launched"
    )
