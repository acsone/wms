# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import traceback

from odoo import models

_logger = logging.getLogger(__name__)


class StockMoveOperationLink(models.Model):

    _inherit = "stock.move.operation.link"

    def unlink(self):
        traceback.extract_stack()
        _logger.info(str(traceback.format_stack()))
        return super(StockMoveOperationLink, self).unlink()
