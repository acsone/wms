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

from openerp import fields, models, api


class StockLocation(models.Model):
    _inherit = 'stock.location'

    kind = fields.Selection(
        [('reserve', 'Reserve'),
         ('parking', 'Parking'),
         ],
        string='Kind')

    def _get_children(self):
        """This method return the list of all children account excluding ids"""
        self._cr.execute("""
            SELECT distinct c.id
            FROM """ + self._table + ' p, ' + self._table + """ c
            WHERE c.parent_left > p.parent_left
              AND c.parent_right < p.parent_right
              AND p.id in %s""", (tuple(self.ids),))
        res = self._cr.fetchall()
        return self.browse(map(lambda x: x[0], res))

    @api.multi
    def write(self, vals):
        """ Update kind of all children location if modified """
        res = super(StockLocation, self).write(vals)
        if vals.get('kind'):
            children = self._get_children()
            super(StockLocation, children).write({'kind': vals['kind']})
        return res
