# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields

from odoo.addons.stock.models.stock_picking import PickingType


class StockPickingTpe(PickingType):

    is_cold = fields.Boolean(help="Check if the picking type implies fridge location")
