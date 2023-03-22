# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.alc_stock_receive_lot.wizards.stock_pack_operation_lot_add import (
    StockPackOperationLotAdd as Base,
)
from odoo.addons.stock.models.stock_lot import StockLot


class StockPackOperationLotAdd(Base):

    tracking = fields.Selection(related="product_id.tracking", readonly=True)
    lot_ids = fields.One2many[StockLot](
        string="Lots",
        related="product_id.lot_ids",
        readonly=True,
    )
