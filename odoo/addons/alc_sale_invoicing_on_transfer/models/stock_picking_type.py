# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.stock.models.stock_picking import PickingType


class StockPickingType(PickingType):

    create_invoice_on_transfer = fields.Boolean(default=False)
