# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class Sale(models.Model):
    _inherit = 'sale.order'

    sale_channel = fields.Selection([
        ('phone', 'Phone'),
        ('mail', 'Mail'),
        ('fax', 'Fax'),
    ])

    sale_channel_visible = fields.Boolean(
        compute='_compute_sale_channel_required'
    )

    @api.depends('team_id')
    def _compute_sale_channel_required(self):
        direct_team = self.env.ref('sales_team.team_sales_department')
        for record in self:
            if direct_team and record.team_id == direct_team:
                record.sale_channel_visible = True
            else:
                record.sale_channel_visible = False

    @api.onchange('team_id')
    def onchange_team_id(self):
        if self.sale_channel_visible and not self.sale_channel:
            self.sale_channel = 'phone'
        elif not self.sale_channel_visible:
            self.sale_channel = False
