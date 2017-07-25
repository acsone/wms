# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping

from ...components.mapper import falsy2emptystring


class CustomerAddressExportMapper(Component):
    _name = 'esb.customer.address.mapper'
    _inherit = ['esb.export.mapper']
    _apply_on = 'res.partner'

    @classmethod
    def _component_match(cls, work):
        return bool(work.timestamp and
                    work.timestamp.kind == 'customer.address')

    direct = [
        (falsy2emptystring('ref'), 'AddressId'),
        (falsy2emptystring('city'), 'City'),
        (falsy2emptystring('name'), 'Firstname'),
    ]

    @mapping
    def compute_optional_fields(self, record):
        """ Manage the direct fields that are optional """
        val = {}
        if record.fax:
            val['Fax'] = record.fax
        if record.phone:
            val['Telephone'] = record.phone
        if record.zip:
            val['Postcode'] = record.zip
        return val

    @mapping
    def compute_customerid(self, record):
        if record.parent_id:
            return {'CustomerId': record.parent_id.ref}
        else:
            return {'CustomerId': ''}

    @mapping
    def compute_street(self, record):
        street = record.street
        if record.street2:
            street += '\n' + record.street2
        return {'Street': street}

    @mapping
    def compute_country_id(self, record):
        if record.country_id:
            return {'CountryId': record.country_id.esb_ref or ''}
        else:
            return {'CountryId': ''}

    @mapping
    def compute_isdefaults(self, record):
        """ If there is only one address for a customer, either invoice or delivery
            then it is also the default for the other type of address
        """
        # Find out if the other type of address exist
        other_type = 'invoice' if record.type == 'delivery' else 'delivery'
        other_exists = self.env['res.partner'].search_count([
            ('parent_id', '=', record.parent_id.id),
            ('type', '=', other_type)])
        return {
            'IsDefaultBilling': ((record.type == 'invoice')
                                 or (other_exists == 0)),
            'IsDefaultShipping': ((record.type == 'delivery')
                                  or (other_exists == 0))
        }


class CustomerAddressCronExporter(Component):

    _name = 'esb.customer.address.cron.exporter'
    _inherit = 'esb.cron.exporter'
    _usage = 'record.exporter.cron'
    _apply_on = 'res.partner'

    @classmethod
    def _component_match(cls, work):
        return bool(work.timestamp and
                    work.timestamp.kind == 'customer.address')

    def get_items_domain(self):
        return [('type', 'in', ['delivery', 'invoice'])]
