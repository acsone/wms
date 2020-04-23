# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockInventory(models.Model):

    _inherit = 'stock.inventory'

    operator_id = fields.Many2one(
        'res.users',
        string='Operator',
        copy=False,
        track_visibility='onchange',
    )

    @api.multi
    def assign_operator(self):
        self.filtered(lambda s: not s.operator_id).write(
            {"operator_id": self.env.user.id}
        )

    @api.multi
    def prepare_inventory(self):
        self.assign_operator()
        return super(StockInventory, self).prepare_inventory()
