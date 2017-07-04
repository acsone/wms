# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


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
