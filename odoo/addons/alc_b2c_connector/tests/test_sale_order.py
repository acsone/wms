# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from psycopg2 import IntegrityError

from odoo.tests.common import SavepointCase


class TestSaleOrder(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestSaleOrder, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.pricelist_id = cls.env.ref("alc_b2c_connector.product_pricelist_b2c")
        # create a b2c_partner
        cls.partner = cls.env["res.partner"].create({"name": "test partner"})

        cls.b2c_order = cls.env["sale.order"].create(
            {"b2c_ref": 10, "sale_channel": "web", "partner_id": cls.partner.id}
        )

    def test_00(self):
        """
           Test Case:
               Create a new SO with the same b2c_ref and channel as the existing
               one
           Expected Result:
               IntegrityError
        """
        with self.assertRaises(IntegrityError):
            self.env["sale.order"].create(
                {"b2c_ref": 10, "sale_channel": "web", "partner_id": self.partner.id}
            )

    def test_01(self):
        """
           Test Case:
               Create a new SO with the same b2c_ref and a different channel
               as the existing one
           Expected Result:
               A new order is created
        """
        self.assertTrue(
            self.env["sale.order"].create(
                {"b2c_ref": 10, "sale_channel": "phone", "partner_id": self.partner.id}
            )
        )
