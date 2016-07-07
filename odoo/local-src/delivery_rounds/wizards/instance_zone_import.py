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

from openerp import models, fields, api


class RoundZoneImport(models.TransientModel):
    _name = 'round.zone.import'

    zone_id = fields.Many2one(
        'res.partner', 'Zone',
        required=True)

    @api.one
    def confirm(self):
        act_close = {'type': 'ir.actions.act_window_close'}
        instance_ids = self._context.get('active_ids')
        if instance_ids is None:
            return act_close
        assert len(instance_ids) == 1, "Only 1 ID expected"
        instance = self.env['round.instance'].browsu(instance_ids)
        #for picking in intervention.picking_ids:
        #    if picking.date_done:
        #        continue
        #    picking.date_done = self.datetime
        #    picking.action_done()
        #intervention.action_picking_delivered()
        return act_close


