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

{
    'name': 'Delivery Rounds',
    'version': '1.0',
    'author': "BCIM",
    'maintainer': 'Camptocamp',
    'category': 'Stock Management',
    'depends': [
        'stock',
        'delivery',
        'stock_picking_subcode',
        ],
    'data': [
        'views/menu.xml',
        'views/vehicle.xml',
        'views/zone.xml',
        'views/instance.xml',
        'views/picking.xml',
        'views/partner.xml',
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'wizards/instance_zone_import.xml',
        'wizards/make_today_delivery_plan.xml',
        'wizards/picking_assign_delivery_round.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
    'application': False,
}
