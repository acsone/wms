# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import api

from odoo.addons.stock.models.stock_quant import StockQuant as StockQuantBase

_logger = logging.getLogger(__name__)


class StockQuant(StockQuantBase):
    @api.model
    def _unlink_zero_quants(self):
        if not self.env.context.get("unlink_zero_quants"):
            _logger.debug(
                "Unlink zero quants ignored to avoid concurrency access. A cron job is "
                "planned instead"
            )
            return False
        return super()._unlink_zero_quants()

    @api.model
    def _quant_tasks(self):
        return super(
            StockQuant, self.with_context(unlink_zero_quants=True)
        )._quant_tasks()
