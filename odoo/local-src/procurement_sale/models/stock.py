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

from openerp import models, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def _action_procurement_create(self):
        return super(SaleOrderLine, self.with_context(recount=True))._action_procurement_create()


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def quants_get_preferred_domain(self, cr, uid, qty, move, ops=False,
                                    lot_id=False, domain=None,
                                    preferred_domain_list=[], context=None):
        if context and context.get('recount'):
            remaining = (move.product_id.qty_available -
                         move.product_id.outgoing_qty)
            qty = min(qty, max(remaining, 0.0))
        return super(StockQuant, self).quants_get_preferred_domain(
            cr, uid, qty, move, ops=ops, lot_id=lot_id, domain=domain,
            preferred_domain_list=[], context=context)
