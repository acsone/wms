# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestReceptionPharmacy(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestReceptionPharmacy, cls).setUpClass()

        # Create customer with delivery address
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test partner",
                "street": "25 rue des bourgeois",
                "zip": "5000",
                "country_id": cls.env.ref("base.be").id,
                "type": "delivery",
            }
        )

        # Create the product for reception
        cls.product = cls.env["product.template"].browse(
            cls.env.ref("specific_stock.product_colis_souverain").id
        )

        cls.bin = cls.env["stock.location"].create({"name": "Test unit"})

        # Instance of reception pharmacy
        cls.ReceptionPharmacy = cls.env["reception.pharmacy"]
        cls.ReceptionPharmacyLine = cls.env["reception.pharmacy.line"]

    def test_00(self):
        # Create reception pharmcy for the given customer
        # assert that the partner_shipping_id = customer delivery id

        reception = self.ReceptionPharmacy.create({"product_id": self.product.id})
        pharmacy_line = self.ReceptionPharmacyLine.create(
            {
                "customer_id": self.partner.id,
                "bin_id": self.bin.id,
                "wizard_id": reception.id,
            }
        )

        self.assertEqual(pharmacy_line.partner_shipping_id.id, self.partner.id)
