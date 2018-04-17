# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.multi
    def check_tracking(self, pack_operation):
        """ By pass checks if serial number. """
        if self.env.context.get('__skip_check_tracking'):
            return
        super(StockMove, self).check_tracking(pack_operation)
