# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import StringIO
import traceback

from odoo import api, models

_logger = logging.getLogger(__name__)


class StockPackOperation(models.Model):

    _inherit = "stock.pack.operation"

    @api.multi
    def unlink(self):
        ids = ["%s" % id for id in self.ids]
        stack = StringIO.StringIO()
        traceback.print_stack(file=stack)
        stack.seek(0)
        _logger.warning("Operations %s deleted \n %s", ", ".join(ids), stack.getvalue())
        return super(StockPackOperation, self).unlink()
