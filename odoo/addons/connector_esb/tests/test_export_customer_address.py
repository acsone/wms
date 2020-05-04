# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os

from .common import ESBXMLTestCase


class ExportCustomerAddressTestCase(ESBXMLTestCase):
    def setUp(self):
        super(ExportCustomerAddressTestCase, self).setUp()
        self.setup_records()
        self.maxDiff = None
        self.timestamp = self.env.ref("connector_esb.esb_timestamp_customer_address")

    @property
    def model(self):
        return self.env["res.partner"]

    def setup_records(self):
        self.country44 = self.env["res.country"].search([("id", "=", 44)])
        self.country44.esb_ref = "ESB"
        self.country_no_ref = self.env["res.country"].search([("id", "=", 33)])
        self.country_no_ref.esb_ref = ""
        self.all_records = self.model.browse()
        # Create a customer with an invoicing address but no delivery address
        self.main_partner = self.model.create(
            {
                "name": "Company 1",
                "street": "Main Street, 2",
                "ref": "1231",
                "zip": "999888",
                "city": "Armagedon",
                "country_id": 44,
                "email": "test@test.be",
            }
        )
        self.all_records |= self.main_partner
        self.main_partner_invoice = self.model.create(
            {
                "ref": "1232",
                "name": "invoicing-address",
                "street": "Some streets in one line",
                "street2": "",
                "zip": "xyz",
                "city": "Somewhere very far away",
                "country_id": 44,
                "phone": "021123123",
                "fax": "",
                "parent_id": self.main_partner.id,
                "type": "invoice",
            }
        )
        self.all_records |= self.main_partner_invoice
        # Create a customer with a delivery address
        self.partner_2 = self.model.create(
            {
                "name": "Company 2",
                "street": "Main Street, 2",
                "ref": "999888",
                "zip": "123123",
                "city": "Paradise",
                "country_id": 44,
                "email": "test2@test.be",
            }
        )
        self.partner_2_delivery = self.model.create(
            {
                "ref": "1233",
                "name": "delivery-address",
                "street": "street 1",
                "street2": "",
                "zip": "zip",
                "city": "TheCity",
                "country_id": 44,
                "parent_id": self.partner_2.id,
                "type": "delivery",
            }
        )
        # Create a supplier that should not be picked by the tests
        self.supplier_1 = self.model.create(
            {
                "name": "Supplier 1",
                "street": "Main Street, 2",
                "ref": "123122424234",
                "zip": "999888",
                "city": "Sale City",
                "country_id": 44,
                "supplier": True,
                "customer": False,
            }
        )
        # And a delivery address for it that should not come up either
        self.supplier_1_delivery = self.model.create(
            {
                "ref": "1233983298324089234",
                "name": "delivery-address",
                "street": "H-Street 432",
                "street2": "",
                "zip": "zip",
                "city": "DaCity",
                "country_id": 44,
                "parent_id": self.supplier_1.id,
                "type": "delivery",
                "supplier": True,
                "customer": False,
            }
        )

    def test_filename(self):
        self.check_filename("CustomerAddress_{0}_{1}.xml")

    def test_mapper_for_billing_address(self):
        """ Generate dict with the mapper and compare with what is expected"""
        expected = {
            "CustomerId": self.main_partner.ref,
            "AddressId": "5",
            "City": self.main_partner_invoice.city,
            "CountryId": self.country44.esb_ref,
            "Firstname": self.main_partner_invoice.name,
            "Postcode": self.main_partner_invoice.zip,
            "Telephone": self.main_partner_invoice.phone,
            "Street": u"Some streets in one line",
            "IsDefaultBilling": True,
            "IsDefaultShipping": False,
        }
        rec = self.main_partner_invoice
        with self.backend.work_on(self.model._name, timestamp=self.timestamp) as work:
            mapper = work.component(usage="export.mapper")
            self.assertDictEqual(
                mapper.map_record(rec).values(
                    customer_id=self.main_partner.ref, address_kind="invoice"
                ),
                expected,
            )

    def test_mapper_for_shipping_address_without(self):
        """ Generate dict with the mapper and compare with what is expected

        No specific shipping address so use the client default
        """
        expected = {
            "CustomerId": self.main_partner.ref,
            # If shipping address does not exist !
            "AddressId": "0",
            "City": self.main_partner.city,
            "CountryId": self.country44.esb_ref,
            "Firstname": self.main_partner.name,
            "Postcode": self.main_partner.zip,
            "Street": self.main_partner.street,
            "IsDefaultBilling": False,
            "IsDefaultShipping": True,
        }
        rec = self.main_partner
        with self.backend.work_on(self.model._name, timestamp=self.timestamp) as work:
            mapper = work.component(usage="export.mapper")
            self.assertDictEqual(
                mapper.map_record(rec).values(
                    customer_id=self.main_partner.ref, address_kind="delivery"
                ),
                expected,
            )

    def test_mapper_for_shipping_address_with(self):
        """ Generate dict with the mapper and compare with what is expected

        A specific shipping address is set for the client
        """
        expected = {
            # Testing empty ref should not be false but empty string
            "CustomerId": self.partner_2.ref,
            # Shipping address exists !
            "AddressId": "12",
            "City": self.partner_2_delivery.city,
            "CountryId": self.country44.esb_ref,
            "Firstname": self.partner_2_delivery.name,
            "Postcode": self.partner_2_delivery.zip,
            "Street": self.partner_2_delivery.street,
            "IsDefaultBilling": False,
            "IsDefaultShipping": True,
        }
        rec = self.partner_2_delivery
        with self.backend.work_on(self.model._name, timestamp=self.timestamp) as work:
            mapper = work.component(usage="export.mapper")
            self.assertDictEqual(
                mapper.map_record(rec).values(
                    customer_id=self.partner_2.ref, address_kind="delivery"
                ),
                expected,
            )

    def test_export(self):
        """ Run export and compare with example file"""
        self.timestamp.writer = "local"
        with self.backend.work_on(self.model._name, timestamp=self.timestamp) as work:
            exporter = work.component(usage="record.exporter.cron")
            respath = exporter.run()
            self.addCleanup(os.remove, respath)
            with open(respath, "r") as result_file:
                result = result_file.read()
            self.assertXmlEquivalentData(
                result, self.read_test_file("customer_address_1.xml"), "City"
            )

    def test_address_incomplete(self):
        """Check that customer with incomplete address are not exported"""
        # Get all existing possible addresses
        with self.backend.work_on(self.model._name, timestamp=self.timestamp) as work:
            exporter = work.component(usage="record.exporter.cron")
            possible_addresses = exporter.get_items(None)
        # Create some invalid ones
        # Partner with no name
        self.model.create(
            {
                "name": "",
                "commercial_partner_id": self.main_partner.id,
                "street": "Main Street, 2",
                "ref": "991",
                "zip": "123123",
                "city": "Paradise",
                "country_id": 44,
                "customer": True,
                "type": "invoice",
            }
        )
        # Partner with no street
        self.model.create(
            {
                "name": "no street",
                "street": "",
                "ref": "992",
                "zip": "123123",
                "city": "Paradise",
                "country_id": 44,
                "type": "delivery",
                "customer": True,
            }
        )
        # Partner with no zip
        self.model.create(
            {
                "name": "no zip",
                "street": "street",
                "ref": "993",
                "zip": None,
                "city": "Paradise",
                "country_id": 44,
                "commercial_partner_id": self.main_partner.id,
                "type": "delivery",
            }
        )
        # Partner with no city
        self.model.create(
            {
                "name": "no zip",
                "street": "street",
                "ref": "994",
                "zip": "2342342",
                "city": "",
                "country_id": 44,
            }
        )
        # Partner with no country
        self.model.create(
            {
                "name": "no zip",
                "street": "street",
                "ref": "995",
                "zip": "2342342",
                "city": "Ville",
            }
        )
        # Partner with country without esb_ref
        self.model.create(
            {
                "name": "no zip",
                "street": "street",
                "ref": "996",
                "zip": "2342342",
                "city": "CiTy",
                "country_id": self.country_no_ref.id,
            }
        )

        with self.backend.work_on(self.model._name, timestamp=self.timestamp) as work:
            exporter = work.component(usage="record.exporter.cron")
            items = exporter.get_items(None)
        self.assertEqual(len(items), len(possible_addresses))
