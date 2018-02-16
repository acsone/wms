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
            return {'CustomerId': record.ref}

    @mapping
    def compute_addressid(self, record):
        """ Map the address id

        The address id for an export should be the ref of the record.
        But if for a customer no specific address exist for invoicing and
        shipping, in the file there would be a duplicate for
        CustomerId/AddressId wich would be a problem for the ESB.
        So for shipping if we do not have a specific address we set it to zero
        """
        address_id = ''
        if record.parent_id:
            address_id = record.ref
        elif self.options.address_kind == 'delivery':
            address_id = '0'
        else:
            address_id = record.ref
        return {'AddressId': address_id}

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
        """Set the type of address being created it is one or the other"""
        is_invoicing_address = self.options.address_kind == 'invoice'
        return {
            'IsDefaultBilling': (is_invoicing_address),
            'IsDefaultShipping': (not is_invoicing_address)
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

    def _prepare_item(self, items):
        prepared = []
        for kind, item in items:
            prepared.append(
                self.mapper.map_record(item).values(address_kind=kind))
        return prepared

    def get_items(self, export_since):
        """Get customer addresses and add type of address to export

        Export for each customer the invoice and delivery address
        And if the specific address does not exist the default address
        of the customer must be used.
        For the mapper to know which address is exported, the type is included
        with each item.
        """
        items = super(CustomerAddressCronExporter,
                      self).get_items(export_since)
        # get_items will return all modified partners including the addresses.
        # Wwe need to get the related parent or children to be sure we include
        # the pair (invoice, delivery), even if they have not been modified.
        # The following search extend the items with the children addresses
        # or the parent.
        items = self.env['res.partner'].search(
                ['|',
                 ('id', 'child_of', items.ids),
                 ('child_ids', 'in', items.ids),
                 ('type', 'in', ('delivery', 'invoice', 'contact')),
                 ],
                order='create_date DESC'
                )
        # group the records by kind of address in dictionaries for fast lookups
        customers = []
        invoice_addresses = {}
        delivery_addresses = {}
        for item in items:
            parent_id = item.parent_id.id
            if item.type == 'invoice':
                if not invoice_addresses.get(parent_id):
                    invoice_addresses[parent_id] = item
            elif item.type == 'delivery':
                if not delivery_addresses.get(parent_id):
                    delivery_addresses[parent_id] = item
            elif item.commercial_partner_id == item:
                # Ignore items of type 'contact' which are children of a
                # partner. E.g. prevent to export 'City Z' as both invoice
                # and delivery for itself in this scenario:
                #   John Doe (contact)
                #   - City X (delivery)
                #   - City Y (invoice)
                #   - City Z (contact)
                customers.append(item)

        # Get the address to export for each kind. We can loop on customers as
        # we did a search for the parent partner previously. Even if only the
        # invoice address has been modified, the parent partner should be
        # in the list.
        items2export = []
        for customer in customers:
            invoice = invoice_addresses.get(customer.id) or customer
            items2export.append(('invoice', invoice))
            delivery = delivery_addresses.get(customer.id) or customer
            items2export.append(('delivery', delivery))

        return items2export

    def get_items_domain(self):
        return [('customer', '=', 1)]
