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


class StockWizardReassort(models.TransientModel):
    _name = 'stock.wizard.reassort'

    @api.multi
    def confirm(self):
        model = self._context['active_model']
        assert model in ('report.stock.quant.bylocation',
                         'report.stock.quant.bylocation.reserve'), \
            "Invalid Model"

        pickings = self.env['stock.picking']
        for report in self.env[model].browse(self._context['active_ids']):
            if model == 'report.stock.quant.bylocation':
                picking = report.create_parking_picking()
            else:
                picking = report.create_reserve_picking()
            pickings |= picking

        if model == 'report.stock.quant.bylocation':
            name = _('Parking')
        else:
            name = _('Reserve')

        action = {
            'name': name,
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_type': 'form',
        }

        if len(pickings) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': picking.id
            })
        else:
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', pickings.ids)]
            })

        return action
