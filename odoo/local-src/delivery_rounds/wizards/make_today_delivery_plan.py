# -*- coding: utf-8 -*-
# © 2016-2017 Jacques-Etienne Baudoux (BCIM)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import Warning


class MakeTodayDeliveryPlan(models.TransientModel):
    _name = 'round.wizard.makeplan'

    template_ids = fields.Many2many(
        'round.template', string='Templates',
        )
    assign_moves = fields.Boolean(
        'Reserve stock', default=True)

    @api.one
    def confirm(self):
        if not self.template_ids:
            raise Warning(_('Please select the templates'))
        templates = self.template_ids
        today = fields.Date.context_today(self)
        # deduct templates for which instance already exist
        instances = self.env['round.instance'].search([
            ('date', '=', today)])
        templates -= instances.mapped('template_id')
        # create instance for each template
        for template in templates:
            self.env['round.instance'].create({
                'template_id': template.id,
                'itinerary_ids': [(6, 0, template.itinerary_ids.ids)],
                'date': today,
                'time_picking_planned': template.time_picking_planned,
                'time_leave_planned': template.time_leave_planned,
                })

        if self.assign_moves:
            # Run stock reservations in background.  This process automatically
            # assign pickings and shippings to available delivery rounds
            self.env['procurement.order.compute.all'].procure_calculation()

        return dict(self.env.ref(
            'delivery_rounds.action_round_instance').read()[0])
