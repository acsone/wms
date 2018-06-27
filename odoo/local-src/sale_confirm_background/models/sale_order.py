# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.addons.queue_job.job import job


class Sale(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(
        selection_add=[('confirm_background', 'Confirm in Background')]
    )

    @job(default_channel='root.background.process')
    @api.multi
    def confirm_in_background(self):
        """Confirm sales order in background"""
        self.ensure_one()
        if self.state != 'confirm_background':
            return
        self.action_confirm()
        action = self.env.ref('sale.action_orders').read()[0]
        action.update({
            'res_id': self.id,
            'views': [(False, 'form')],
        })
        self.env.user.notify_info(
            _('Order %s is now confirmed.') % self.name,
            sticky=True,
            action=action,
        )

    def action_confirm_background(self):
        self.write({
            'state': 'confirm_background',
        })
        for order in self:
            self.env.user.notify_info(
                _('Order %s will be confirmed in background.') % order.name,
            )
            order.with_delay(
                description=_(
                    'Confirmation of sales order %s'
                ) % order.name,
            ).confirm_in_background()
