# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from odoo.osv.expression import AND

from ...components.mapper import falsy2emptystring


class CustomerAddressExportMapper(Component):
    _name = "esb.customer.address.mapper"
    _inherit = ["esb.export.mapper"]
    _apply_on = "res.partner"

    @classmethod
    def _component_match(cls, work):
        return bool(work.timestamp and work.timestamp.kind == "customer.address")

    direct = [(falsy2emptystring("city"), "City")]

    @mapping
    def compute_name(self, record):
        try:
            name = record.name_get()[0][1]
        except TypeError:
            name = record.name
        return {"Firstname": name or ""}

    @mapping
    def compute_optional_fields(self, record):
        """ Manage the direct fields that are optional """
        val = {}
        if record.fax:
            val["Fax"] = record.fax
        if record.phone:
            val["Telephone"] = record.phone
        if record.zip:
            val["Postcode"] = record.zip
        return val

    @mapping
    def compute_customerid(self, record):
        return {"CustomerId": self.options.customer_id or ""}

    @mapping
    def compute_addressid(self, record):
        """ Map the address id

        The address id for an export should be the ref of the record.
        But if for a customer no specific address exist for invoicing and
        shipping, in the file there would be a duplicate for
        CustomerId/AddressId wich would be a problem for the ESB.
        So for shipping if we do not have a specific address we set it to zero.

        The ref value on a customer record and a specific address for that
        customer is always the same (see module base_partner_sequence).
        So for specific invoice and delivery address instead of using the ref
        field we use constants value which are not used in ref.

        """

        INVOICE_REF = "5"
        DELIVERY_REF = "12"

        if record.parent_id:
            if self.options.address_kind == "delivery":
                address_id = DELIVERY_REF
            elif self.options.address_kind == "invoice":
                address_id = INVOICE_REF
        elif self.options.address_kind == "delivery":
            address_id = "0"
        else:
            address_id = record.ref
        return {"AddressId": address_id or ""}

    @mapping
    def compute_street(self, record):
        street = record.street or ""
        if record.street2:
            street += "\n" + record.street2
        return {"Street": street or ""}

    @mapping
    def compute_country_id(self, record):
        if record.country_id:
            return {"CountryId": record.country_id.esb_ref or ""}
        else:
            return {"CountryId": ""}

    @mapping
    def compute_isdefaults(self, record):
        """Set the type of address being created it is one or the other"""
        is_invoicing_address = self.options.address_kind == "invoice"
        return {
            "IsDefaultBilling": (is_invoicing_address),
            "IsDefaultShipping": (not is_invoicing_address),
        }


class CustomerAddressCronExporter(Component):

    _name = "esb.customer.address.cron.exporter"
    _inherit = "esb.cron.exporter"
    _usage = "record.exporter.cron"
    _apply_on = "res.partner"

    @classmethod
    def _component_match(cls, work):
        return bool(work.timestamp and work.timestamp.kind == "customer.address")

    def _prepare_item(self, items):
        prepared = []
        for customer_id, kind, item in items:
            prepared.append(
                self.mapper.map_record(item).values(
                    customer_id=customer_id, address_kind=kind
                )
            )
        return prepared

    def _valid_address_domain(self):
        """All address that are sent must be valid."""
        return [
            ("city", "!=", ""),
            ("name", "!=", ""),
            ("zip", "!=", ""),
            ("street", "!=", ""),
            ("country_id.esb_ref", "!=", ""),
        ]

    def get_items(self, export_since):
        """Get customer addresses and add type of address to export

        Export for each customer the invoice and delivery address
        For the mapper to know which address for which customer is exported,
        the type and customer ref is included with each item.
        To find the correct address the default Odoo method is used so for one
        customer the same delivery/invoice addresses are seen on Odoo and
        Magento.
        This default method address_get has been monkey patched for Alcyon.
        """
        items = super(CustomerAddressCronExporter, self).get_items(export_since)
        modified_items_ids = set(items.mapped("id"))
        # get_items will return all modified customer including the addresses.
        # Then for all commercial partner with potentially modified addresses.
        commercial_partners = items.mapped("commercial_partner_id")
        # Search for the impacted customers in their structure.
        possible_impacted_customer = self.env["res.partner"].search(
            [
                ("commercial_partner_id", "in", commercial_partners.ids),
                ("customer", "=", True),
                ("email", "<>", False),
            ]
        )
        items2export = []
        for customer in possible_impacted_customer:
            # For each customer get the invoice and devlivery addresses
            addresses = customer.address_get(("invoice", "delivery"))
            # If one of them has changed
            impacting_records = set(addresses.values())
            if not modified_items_ids.intersection(impacting_records):
                continue
            # Export them. Together as they are always sent in pair.
            items2export.append(
                (
                    customer.ref,
                    "invoice",
                    self.env["res.partner"].browse(addresses["invoice"]),
                )
            )
            items2export.append(
                (
                    customer.ref,
                    "delivery",
                    self.env["res.partner"].browse(addresses["delivery"]),
                )
            )
        return items2export

    def get_items_domain(self):
        """Find all records that can be used as customer addresses."""
        domain = ["|", ("customer", "=", 1), ("type", "in", ["invoice", "delivery"])]
        return AND([domain, self._valid_address_domain()])

    def run(self, export_since=None, max_records=0):
        """ Run the export.

        Redefined because the get_items does not return a simple
        recordset but a list of tuples, and can not be handled by the _lock.

        """
        items = self.get_items(export_since=export_since)
        return self._export_items(items)
