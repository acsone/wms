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

from openerp import api, models, _
from openerp.exceptions import Warning


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.one
    def button_fillwithstock(self):
        # check source location has no children, i.e. we scanned a bin
        if self.location_id.child_ids:
            raise Warning(_('Please choose a source end location'))
        if self.move_lines:
            raise Warning(_('Moves lines already exsits'))
        quants = self.env['stock.quant'].search([
            ('location_id', '=', self.location_id.id),
            # ('reservation_id', '=', False),
            ('qty', '>', 0.0)])
        quants_reserved = []
        products_available = {}
        for quant in quants:
            if quant.reservation_id:
                quants_reserved.append(quant)
                continue
            if quant.product_id.id not in products_available:
                products_available[quant.product_id.id] = {
                    'picking_id': self.id,
                    'product_id': quant.product_id.id,
                    'name': quant.product_id.partner_ref,
                    'product_uom_qty': quant.qty,
                    'product_uom': quant.product_uom_id.id,
                    'picking_type_id': self.picking_type_id.id,
                    'location_id': self.location_id.id,
                    'location_dest_id': self.location_dest_id.id,
                    }
            else:
                products_available[quant.product_id.id]['product_uom_qty'] += quant.qty
        move_obj = self.env['stock.move']
        if not products_available:
            raise Warning(_('Nothing to move'))
        for data in products_available.values():
            move_obj.create(data)
        self.action_confirm()
        self.action_assign()

        products_reserved = {}
        for quant in quants_reserved:
            if quant.product_id.id not in products_reserved:
                products_reserved[quant.product_id.id] = {
                    'picking_id': self.id,
                    'product_id': quant.product_id.id,
                    'product_qty': quant.qty,
                    'product_uom_id': quant.product_uom_id.id,
                    'location_id': self.location_id.id,
                    'location_dest_id': self.location_id.id,
                    # 'from_loc': self.location_id.name,
                    # 'to_loc': self.location_id.name,
                    'lots_visible': self.product_id.tracking != 'none',
                    'fresh_record': False,
                    }
            else:
                products_reserved[quant.product_id.id]['product_qty'] += quant.qty
        pack_obj = self.env['stock.pack.operation']
        for data in products_reserved.values():
            pack_obj.create(data)

