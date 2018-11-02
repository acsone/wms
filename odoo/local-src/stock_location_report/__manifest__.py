# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Location Report',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Warehouse',
    'depends': [
        'specific_stock',
    ],
    'data': [
        'views/report_location.xml',
        'views/report_location_barcode.xml',
        'views/paperformat.xml',
    ],
    'installable': True,
}
