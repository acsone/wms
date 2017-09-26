# -*- coding: utf-8 -*-
# © 2016-2017 Jacques-Etienne Baudoux (BCIM)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import Warning


class MakeTodayDeliveryPlan(models.TransientModel):
    _name = 'round.wizard.makeplan'

    version_id = fields.Many2one(
        'round.template.version',
        required=True,
        default=lambda x: x.env['round.template.version'].search(
            [('is_default_version', '=', True)])
    )
    assign_moves = fields.Boolean(
        'Reserve stock', default=True)
    tag_ids = fields.Many2many('round.tag', string='Tags')

    @api.one
    def confirm(self):
        templates = self.version_id.template_ids
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
                'tag_ids': [(6, 0, self.tag_ids.ids)]
                })

        if self.assign_moves:
            # Run stock reservations in background.  This process automatically
            # assign pickings and shippings to available delivery rounds
            self.env['procurement.order.compute.all'].procure_calculation()

        return dict(self.env.ref(
            'delivery_rounds.action_round_instance').read()[0])
