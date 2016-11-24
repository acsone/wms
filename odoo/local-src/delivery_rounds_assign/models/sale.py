# -*- coding: utf-8 -*-
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

from openerp import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def _action_procurement_create(self):
        res = super(SaleOrderLine, self)._action_procurement_create()
        for picking in self.mapped('order_id.picking_ids').filtered(
                lambda x: x.picking_type_subcode == 'PICK'):
            if picking.delivery_round_id:
                continue
            delivery_round = self.env['round.instance'].find(
                picking.partner_id)
            if delivery_round:
                # a delivery round has been found, we reserve for this new move
                if picking.state == 'confirmed' or (
                        picking.state in ['partially_available', 'waiting'] and
                        not picking.printed):
                    picking.do_unreserve()
                    picking.action_assign()
        return res
