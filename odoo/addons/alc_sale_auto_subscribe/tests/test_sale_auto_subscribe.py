# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import unittest

from odoo.tests.common import TransactionCase


@unittest.skip("This test is not working since functionality is disabled")
class TestSaleAutoSubscribe(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_callcenter = cls.env.ref("alc_sale_auto_subscribe.alc_user_callcenter")

    def test_auto_subscribe(self):
        """
        Test case:

        - Create a sale order
        - Check that the callcenter user is auto subscribed to the sale order
        """
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.env.ref("base.res_partner_2").id,
                "partner_invoice_id": self.env.ref("base.res_partner_2").id,
                "partner_shipping_id": self.env.ref("base.res_partner_2").id,
            }
        )
        self.assertIn(
            self.user_callcenter.partner_id.id, sale_order.message_partner_ids.ids
        )
