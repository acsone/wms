# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.addons.alc_stock_receive_lot.wizards.stock_pack_operation_lot_add import StockPackOperationLotAdd as Base


class StockPackOperationLotAdd(Base):

    package_type_id = fields.Many2one(
        related="product_id.product_tmpl_id.package_type_id",
        readonly=True,
    )
