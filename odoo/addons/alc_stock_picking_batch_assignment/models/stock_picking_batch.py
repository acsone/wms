# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _

from odoo.addons.stock_picking_batch.models.stock_picking_batch import (
    StockPickingBatch as StockPickingBatchBase,
)


class StockPickingBatch(StockPickingBatchBase):

    _sql_constraints = [
        (
            "user_id_unique",
            "EXCLUDE (user_id WITH =) WHERE ( user_id is not null and state not in "
            "('done', 'cancel', 'draft'))",
            _("This operator is already assigned to a batch"),
        )
    ]
