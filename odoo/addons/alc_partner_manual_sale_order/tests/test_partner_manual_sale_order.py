# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestPartnerManualSaleOrder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        """The purpose of these tests is to make sure that the domain set on the partner.

        field is not evaluated with crud operations
        """
        super().setUpClass()
        cls.partner_manual_sale_order = cls.env["res.partner"].create(
            {"name": "manual sale order allowed", "manual_sale_order_allowed": True}
        )
        cls.partner_no_manual_sale_order = cls.env["res.partner"].create(
            {"name": "no manual sale order allowed", "manual_sale_order_allowed": False}
        )

    def setUp(self):
        """Test create."""
        super().setUp()
        self.order = self.env["sale.order"].create(
            {"partner_id": self.partner_no_manual_sale_order.id}
        )

    def test_00(self):
        """Test read."""
        res = self.order.read(["partner_id"])
        self.assertEqual(res[0].get("partner_id")[1], "no manual sale order allowed")

    def test_01(self):
        """Test write."""
        self.order.partner_id = self.partner_manual_sale_order
        self.order.partner_id = self.partner_no_manual_sale_order
        self.test_00()
