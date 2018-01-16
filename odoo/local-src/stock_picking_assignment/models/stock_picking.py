# -*- coding: utf-8 -*-
# © 2016 Sylvain Van Hoof (Okia sprl) <sylvain@okia.be>
# © 2016-2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # Odoo Fix: never copy the printed field. Important for backorder creation
    printed = fields.Boolean(copy=False)

    operator_id = fields.Many2one('res.users', string='Operator', copy=False)

    @api.multi
    def assign_operator(self):
        self.write({
            'operator_id': self.env.uid,
            'printed': True,
        })
