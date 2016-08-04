# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Jacques-Etienne Baudoux <je@bcim.be>
#    Copyright (C) 2015-TODAY BCIM <http://www.bcim.be>.
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
from openerp import _, models, fields, api
from openerp.exceptions import Warning


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    grn_id = fields.Many2one(
        comodel_name='stock.grn',
        string='Goods Received Note',
        copy=False,
        readonly=True,  # states={'done': [('readonly', True)]},
    )

#     @api.multi
#     def do_transfer(self):
#         if self.picking_type_code == 'incoming' and not self.grn_id:
#             raise Warning(_('You must attach a Goods Received Note'))
#         return super(StockPicking, self).do_transfer()


# class StockMove(models.Model):
#     _inherit = 'stock.move'
#
#     grn_id = fields.Many2one(
#         comodel_name='stock.grn',
#         string='Goods Received Note',
#         store=True,
#         related='picking_id.grn_id'
#     )
