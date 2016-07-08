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
        'round.zone', 'Zone',
        required=True)

    @api.one
    def confirm(self):
        act_close = {'type': 'ir.actions.act_window_close'}
        instance_ids = self._context.get('active_ids')
        if instance_ids is None:
            return act_close
        assert len(instance_ids) == 1, "Only 1 ID expected"
        instance = self.env['round.instance'].browse(instance_ids)
        partner_ids = self.zone_id.partner_position_ids.mapped('partner_id.id')
        positions = {}
        for pos in self.zone_id.partner_position_ids:
            positions[pos.partner_id.id] = pos.sequence

        instance.zone_ids += self.zone_id

        # call Try to reserve from stock the qty for confirmed pickings
        picking_confirmed = self.env['stock.picking'].search([
            ('partner_id', 'in', partner_ids),
            ('state', '=', 'confirmed')])
        picking_confirmed.action_assign()

        # retrieve all pickings (partially) available not yet bound to a delivery round
        pickings = self.env['stock.picking'].search([
            ('delivery_round_id', '=', False),
            ('partner_id', 'in', partner_ids),
            # ('state', 'in', ('confirmed', 'partially_available', 'assigned'))])
            ('state', 'in', ('partially_available', 'assigned'))])
        pickings.write({'delivery_round_id': instance.id})

        # set sequence on deliveries according to sequence defined in the zone
        shippings = instance.shipping_ids
        last_seq = max([1] + shippings.mapped('sequence'))
        for shipping in shippings:
            if not shipping.sequence:
                shipping.sequence = last_seq + positions[shipping.partner_id.id]

        return act_close
