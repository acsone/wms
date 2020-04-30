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

from odoo import api, fields, models


class RoundItineraryImport(models.TransientModel):
    _name = 'round.itinerary.import'

    itinerary_id = fields.Many2one(
        'round.itinerary', 'Itinerary', required=True
    )

    @api.one
    def confirm(self):
        act_close = {'type': 'ir.actions.act_window_close'}
        instance_ids = self._context.get('active_ids')
        if instance_ids is None:
            return act_close
        assert len(instance_ids) == 1, "Only 1 ID expected"
        instance = self.env['round.instance'].browse(instance_ids)
        instance._include_itinerary(self.itinerary_id)
        return act_close
