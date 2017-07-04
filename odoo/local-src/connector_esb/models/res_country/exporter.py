# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class PharmacyExportMapper(Component):
    _name = 'esb.res.country.mapper'
    _inherit = ['esb.export.mapper']
    _apply_on = 'res.country'

    direct = [
        ('Country', 'Id'),
        ('name', 'Name'),
        ('zip', 'Postcode'),
        ('city', 'City'),
        #('country_id', 'CountryId'),
        ('phone', 'Telephone'),
        ('fax', 'Fax'),
        ('email', 'Email')
    ]

    @mapping
    def compute_country_id(self, record):
        return {'CountryId': record.country_id.id}

    @mapping
    def compute_street(self, record):
        street = record.street
        if record.street2:
            street += '\r\n' + record.street2
        return {'Street' : street}


class PharmacyCronExporter(Component):

    _name = 'esb.pharmacy.cron.exporter'
    _inherit = 'esb.cron.exporter'
    _usage = 'record.exporter.cron'
    _apply_on = 'res.partner'

    def get_items_domain(self):
        all_pharma = self.env['res.partner'].search([('pharmacist_id', '!=', False)])
        pharma = all_pharma.mapped('pharmacist_id')
        domain = [
            ('id', 'in', pharma.ids),
        ]
        return domain
