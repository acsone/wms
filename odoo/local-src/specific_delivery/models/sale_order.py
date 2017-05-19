# -*- coding: utf-8 -*-
# Copyright 2017 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    delivery_round_id = fields.Many2one(
        related='carrier_id.delivery_round_id',
        readonly=True,
    )

    @api.multi
    def action_confirm(self):
        result = super(SaleOrder, self).action_confirm()
        self.picking_ids.write({
            'delivery_round_id': self.delivery_round_id.id,
        })
        return result
