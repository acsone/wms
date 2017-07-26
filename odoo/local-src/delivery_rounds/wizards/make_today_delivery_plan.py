
# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Jacques-Etienne Baudoux <je@bcim.be>
#    Copyright 2016 BCIM sprl, Camptocamp
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

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
            ri = self.env['round.instance'].create({
                'template_id': template.id,
                'date': today,
                'time_picking_planned': template.time_picking_planned,
                'time_leave_planned': template.time_leave_planned,
                })
            for itinerary in template.itinerary_ids:
                rzi = self.env['round.itinerary.import'].create({
                    'itinerary_id': itinerary.id})
                rzi.with_context(
                    active_ids=[ri.id],
                    skip_reservation=True).confirm()

        if self.assign_moves:
            # run in background
            self.env['procurement.order.compute.all'].procure_calculation()

        return dict(self.env.ref(
            'delivery_rounds.action_round_instance').read()[0])
