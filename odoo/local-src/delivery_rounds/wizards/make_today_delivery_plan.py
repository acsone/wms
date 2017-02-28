
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

    vehicle_ids = fields.Many2many(
        'round.vehicle', string='Vehicles',
        )
    assign_moves = fields.Boolean(
        'Reserve stock', default=True)

    @api.one
    def confirm(self):
        if not self.vehicle_ids:
            raise Warning(_('Please select the vehicles'))
        if self.assign_moves:
            user = self.env['res.users'].browse(self._uid)
            self.pool['procurement.order'].run_scheduler(
                self._cr, self._uid,
                company_id=user.company_id.id,
                context=self._context)

        vehicles = self.vehicle_ids
        today = fields.Date.context_today(self)
        # deduct vehicles for which instance already exist
        instances = self.env['round.instance'].search([
            ('date', '=', today)])
        vehicles -= instances.mapped('vehicle_id')
        # create instance for each vehicle
        for vehicle in vehicles:
            ri = self.env['round.instance'].create({
                'vehicle_id': vehicle.id,
                'date': today,
                'time': vehicle.time,
                })
            for zone in vehicle.zone_ids:
                rzi = self.env['round.zone.import'].create({
                    'zone_id': zone.id})
                rzi.with_context(active_ids=[ri.id]).confirm()
        return dict(self.env.ref(
            'delivery_rounds.action_round_instance').read()[0])
