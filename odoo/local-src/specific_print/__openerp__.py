# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Jacques-Etienne Baudoux <je@bcim.be>
#    Copyright 2017 BCIM sprl, Camptocamp
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
    'name': 'Stock Print',
    'version': '1.0',
    'category': 'Stock Management',
    'author': "BCIM",
    'maintainer': 'Camptocamp',
    'depends': [
        'stock',
        'base_report_to_printer',  # OCA/report-print-send.gi
        'stock_receive_lot',
        ],
    'data': [
        'views/stock.xml',
        'views/stock_splitlot.xml',
        'wizards/stock_receive.xml',
        'report/stock_product_label.xml',
        'report/stock_pack_label.xml',
        ],
    'installable': True,
    'license': 'AGPL-3',
    'application': False,
}
