# -*- coding: utf-8 -*-
# Copyright 2017 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    delivery_round_id = fields.Many2one(
        comodel_name='round.instance',
        string='Delivery round',
        readonly=True,
    )

    @api.multi
    def action_confirm(self):
        result = super(SaleOrder, self).action_confirm()
        if self.carrier_id:
            template = self.carrier_id.delivery_template_id
            delivery_round = self.env['round.instance'].search(
                [
                    ('template_id', '=', template.id),
                    ('state', '!=', 'done')
                ],
                order='date asc, time_leave_planned asc',
                limit=1,
            )
            if delivery_round:
                self.delivery_round_id = delivery_round.id
                self.picking_ids.write({
                    'delivery_round_id': self.delivery_round_id.id,
                })
        return result
