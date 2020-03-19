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

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PickingAssignDeliveryRound(models.TransientModel):
    _name = 'picking.assign.delivery.round'

    delivery_round_id = fields.Many2one(
        'round.instance',
        'Delivery Round',
        domain="[('state', 'not in', ('delivering','done'))]",
        required=True,
        ondelete="cascade",
    )

    @api.one
    def confirm(self):
        act_close = {'type': 'ir.actions.act_window_close'}
        shippings = self.env['stock.picking'].browse(
            self._context.get('active_ids')
        )
        if not shippings:
            return act_close
        pickings = shippings._get_all_src_pickings().filtered(
            lambda x: x.picking_type_subcode == 'PICK'
        )
        old_round_instance_customers = shippings.mapped(
            'delivery_round_customer_id'
        )
        pickings_assigned = self.delivery_round_id.with_context(
            manual_change_delivery_round=True
        )._assign_pickings(pickings)
        if not pickings_assigned:
            raise UserError(
                _(
                    'No products available.\n'
                    'Cannot assign the delivery round to the picking'
                )
            )
        old_round_instance_customers.sudo()._remove_if_empty()
        shippings.message_post(
            _('Delivery round "%s" manually assigned')
            % self.delivery_round_id.display_name
        )
        return act_close
