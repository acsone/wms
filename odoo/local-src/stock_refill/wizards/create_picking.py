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

from odoo import api, models, _
from odoo.exceptions import Warning


class StockWizardReassort(models.TransientModel):
    _name = 'stock.wizard.reassort'

    @api.multi
    def confirm(self):
        model = self._context['active_model']
        assert model == 'report.stock.quant.bylocation.reserve', \
            "Invalid Model"
        for report in self.env[model].browse(self._context['active_ids']):
            picking_type = report.location_id.barcode_picking_type_id
            if not picking_type:
                raise Warning(_('Missing Operation Type on Location %s') %
                              report.location_id.display_name)
            picking = self.env['stock.picking'].create({
                'move_type': 'direct',
                'company_id': report.location_id.company_id.id,
                'picking_type_id': picking_type.id,
                'origin': 'reassort',
                'location_id': report.location_id.id,
                'location_dest_id': picking_type.default_location_dest_id.id,
                })
            self.env['stock.move'].create({
                'name': report.product_id.display_name,
                'picking_id': picking.id,
                'product_id': report.product_id.id,
                'product_uom': report.product_id.uom_id.id,
                'product_uom_qty': report.qty,
                'location_id': report.location_id.id,
                'location_dest_id': picking_type.default_location_dest_id.id,
                })
            self.pool['stock.picking'].action_assign(
                self._cr, self._uid, [picking.id], self._context)
