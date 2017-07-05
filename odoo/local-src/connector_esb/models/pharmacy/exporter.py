# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class PharmacyExportMapper(Component):
    _name = 'esb.pharmacy.mapper'
    _inherit = ['esb.export.mapper']
    _apply_on = 'res.partner'

    direct = [
        ('ref', 'Id'),
        ('name', 'Name'),
        ('zip', 'Postcode'),
        ('city', 'City'),
        ('phone', 'Telephone'),
        ('fax', 'Fax'),
        ('email', 'Email')
    ]

    @mapping
    def compute_country_id(self, record):
        return {'CountryId': record.country_id.code}

    @mapping
    def compute_street(self, record):
        street = record.street
        if record.street2:
            street += '\r' + record.street2
        return {'Street': street}


class PharmacyCronExporter(Component):

    _name = 'esb.pharmacy.cron.exporter'
    _inherit = 'esb.cron.exporter'
    _usage = 'record.exporter.cron'
    _apply_on = 'res.partner'

    def get_items_domain(self):

        # Get the timestamp of the last export executed
        last_export_time = self.env['esb.backend.timestamp'].get_last_export_time(
            self.model._name, self.collection.id, '')
        # Get all the partner with a pharmacist
        all_pharma = self.env['res.partner'].search(
                [('pharmacist_id', '!=', False)])
        # If exported before, keep the pharmacist that have changed since
        if last_export_time:
            all_pharma = all_pharma.filtered(
                    lambda r: r.pharmacist_id.write_date > last_export_time)
        pharma = all_pharma.mapped('pharmacist_id')
        domain = [
            ('id', 'in', pharma.ids),
        ]
        return domain
