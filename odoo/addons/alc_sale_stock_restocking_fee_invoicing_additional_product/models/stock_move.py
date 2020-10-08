# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockMove(models.Model):

    _inherit = "stock.move"

    @api.multi
    def _is_restocking_fee_chargeable(self):
        self.ensure_one()
        if self.is_additional_move:
            return False
        return super(StockMove, self)._append_move_to_charge()
