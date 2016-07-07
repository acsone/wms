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

from openerp import _, api, exceptions, fields, models


class RoundZone(models.Model):
    _name = 'round.zone'

    name = fields.Char('Name', required=True)
    code = fields.Char('Code')
    partner_position_ids = fields.One2many(
        'round.zone.position', 'zone_id', 'Partners')
    vehicle_id = fields.Many2one(
        'round.vehicle', 'Vehicle',
        ondelete='restrict')


class RoundZonePosition(models.Model):
    _name = 'round.zone.position'
    _rec_name = 'zone_id'
    _order = 'sequence'

    zone_id = fields.Many2one(
        'res.partner', 'Zone',
        ondelete='cascade')
    sequence = fields.Integer('Sequence')
    partner_id = fields.Many2one(
        'res.partner', 'Partner',
        required=True,
        ondelete='restrict',
        domain=[('customer', '=', True)])
