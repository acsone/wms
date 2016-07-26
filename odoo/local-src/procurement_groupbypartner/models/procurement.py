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

from openerp import api, fields, models


class ProcurementRule(models.Model):
    _inherit = 'procurement.rule'

    group_propagation_groupbypartner = fields.Boolean(
        'Propagate group by partner')


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.model
    def _run_move_create(self, procurement):
        vals = super(ProcurementOrder, self)._run_move_create(procurement)
        if procurement.rule_id.group_propagation_option == 'propagate':
            if (vals['partner_id'] and
                    procurement.rule_id.group_propagation_groupbypartner):
                groups = self.env['procurement.group'].search(
                    [('partner_id', '=', vals['partner_id'])],
                    order='id',
                    limit=1)
                vals['group_id'] = groups[0].id
        return vals
