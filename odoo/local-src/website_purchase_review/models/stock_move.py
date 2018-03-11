# -*- coding: utf-8 -*-
# © 2018 Okia SPRL <Sylvain Van Hoof>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    validation_date = fields.Datetime('Validation date')

    @api.constrains('state')
    def set_validation_date(self):
        for move in self:
            if move.state != 'done':
                continue
            move.validation_date = fields.Datetime.now()
