# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class ProductExportMapper(Component):
    _name = 'esb.product.mapper'
    _inherit = ['esb.export.mapper']
    _apply_on = 'product.product'

    direct = [
        ('name', 'Gesdem'),
        ('default_code', 'Gesart'),
        ('barcode', 'Cplz05'),
        ('weight', 'Gespnt'),
    ]

    translatable_keys = {
        'nl_BE': {
            'name': 'Refdem',
        }
    }

    @mapping
    def supplier(self, record):
        supplier_code = ''
        suppliers = record.seller_ids
        if suppliers:
            supplier_code = suppliers[0].product_code
        return {'Gesarc': supplier_code}

    @mapping
    def fixed_fields(self, record):
        """ return hardcoded values for fields """
        empty = ('Cp2z22', 'Warceg', 'Warcfr', 'Warcnl')
        zero = ('Gescsg', 'Cp2z02', 'Cp2z23', 'Cp2z24', 'Cplz29',
                'Cp2z17', 'Cp2z19')
        values = {f: '' for f in empty}
        values.update({f: 0 for f in zero})
        return values

    @mapping
    def todo(self, record):
        """ TODO: fields to map, hardcoded for now """
        return {
            'Gesfou': '',
            'Cplz25': '',
            'Gesunv': '',
            'Gescrt': '2017/07/04',
            'Cplz19': '1',
            'Gescde': '1',
            'Cp2z08': '1.0',
            'Gesctv': '',
            'Gescsa': '1',
            'LotEch': '2017/11/16',
            'Cplz03': '',
            'Gescge': '0',
            'Gescov': '',
            'Cplz07': '',
            'Cplz14': '',
            'Cp2z01': '2.0',
            'Cp2z03': '2.5',
            'Cp2z05': '3.0',
            'GMA': '',
            'ALI': '',
            'ALG': '',
            'ALH': '',
            'IMP': '',
        }


class ProductCronExporter(Component):

    _name = 'esb.product.cron.exporter'
    _inherit = ['esb.cron.exporter', ]
    _usage = 'record.exporter.cron'
    _apply_on = 'product.product'

    def get_items_domain(self):
        domain = [
            # GESCHR!=’L’ (non livrables)
            # TODO: which field/attribute/condition is this???
            # not GESTART.startwith(‘8888’) (contrib antibio)
            ('default_code', 'not like', '8888%'),
            # Articles créés depuis 29/7/2014
            ('create_date', '>', '2014-7-29 00:00:00'),
        ]
        return domain
