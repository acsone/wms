# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.alc_stock_receive_lot.wizards.stock_pack_operation_lot_add import (
    StockPackOperationLotAdd as Base,
)
from odoo.addons.stock_lot_is_archived.models.stock_lot import StockLot


class StockPackOperationLotAdd(Base):

    tracking = fields.Selection(related="product_id.tracking", readonly=True)
    lot_ids = fields.One2many[StockLot](
        string="Lots",
        compute="_compute_lot_ids",
        readonly=True,
    )

    @api.depends("product_id", "product_id.lot_ids")
    def _compute_lot_ids(self):
        for rec in self:
            rec.lot_ids = rec.product_id.lot_ids.filtered(
                lambda lot: not lot.is_archived
            )
