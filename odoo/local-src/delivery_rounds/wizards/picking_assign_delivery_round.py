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


class PickingAssignDeliveryRound(models.TransientModel):
    _name = 'picking.assign.delivery.round'

    delivery_round_id = fields.Many2one(
        'round.instance', 'Delivery Round',
        domain="[('state', 'in', ('draft', 'open'))]",
        required=True)

    @api.one
    def confirm(self):
        act_close = {'type': 'ir.actions.act_window_close'}
        shipping_ids = self._context.get('active_ids')
        if shipping_ids is None:
            return act_close
        shipping = self.env['stock.picking'].browse(shipping_ids)
        shipping.delivery_round_id = self.delivery_round_id
        # make reservation
        for picking in shipping._get_all_from_pickings().filtered(
                lambda x: x.picking_type_subcode == 'PICK'):
            if picking.state == 'confirmed' or (
                    picking.state in ['partially_available', 'waiting'] and
                    not picking.printed):
                picking.do_unreserve()
                picking.action_assign()
        return act_close
