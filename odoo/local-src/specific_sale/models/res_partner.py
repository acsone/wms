# -*- coding: utf-8 -*-
# © 2017 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def _compute_sale_lines_count(self):
        for partner in self:
            domain = [
                ('state', 'in', ['sale']),
                ('order_id.partner_id', '=', partner.id)
            ]

            partner.sale_lines_count = len(
                self.env['sale.order.line'].search(domain)
            )

    sale_lines_count = fields.Integer(
        compute='_compute_sale_lines_count'
    )

    @api.multi
    def action_view_sale_lines_unavailable(self):
        self.ensure_one()

        action_data = self.env.ref(
            'specific_sale.action_sale_lines_unavailable_list'
        ).read()[0]
        action_data['domain'] = [
            ('state', 'in', ['sale']),
            ('order_id.partner_id', '=', self.id)
        ]

        return action_data
