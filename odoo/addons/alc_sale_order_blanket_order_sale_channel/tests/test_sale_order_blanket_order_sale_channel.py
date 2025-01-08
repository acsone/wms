# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import freezegun

from odoo.addons.sale_order_blanket_order.tests.common import SaleOrderBlanketOrderCase


class TestSaleOrderBlanketOrderSaleChannel(SaleOrderBlanketOrderCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "partner"})
        cls.channel = cls.env["sale.channel"].create({"name": "channel"})
        cls.team = cls.env["crm.team"].create(
            {"name": "team", "sale_channel_id": cls.channel.id}
        )

    @freezegun.freeze_time("2025-02-01")
    def test_00(self):
        self.blanket_so.action_confirm()
        self.assertFalse(self.blanket_so.call_off_order_ids)
        order = self.env["sale.order"].create(
            {
                "order_type": "call_off",
                "date_order": "2025-02-01",
                "partner_id": self.partner.id,
                "blanket_order_id": self.blanket_so.id,
                "team_id": self.team.id,
            }
        )
        self.assertEqual(order.sale_channel_id, self.channel)
        order.action_confirm()
        self.assertTrue(self.blanket_so.call_off_order_ids)
        self.assertEqual(
            self.blanket_so.call_off_order_ids.sale_channel_id, self.channel
        )

    @freezegun.freeze_time("2025-02-01")
    def test_01(self):
        self.blanket_so.action_confirm()
        self.assertFalse(self.blanket_so.call_off_order_ids)
        order = self.env["sale.order"].create(
            {
                "order_type": "call_off",
                "date_order": "2025-02-01",
                "partner_id": self.partner.id,
                "blanket_order_id": self.blanket_so.id,
            }
        )
        self.assertFalse(order.sale_channel_id)
        order.action_confirm()
        self.assertTrue(self.blanket_so.call_off_order_ids)
        self.assertFalse(self.blanket_so.call_off_order_ids.sale_channel_id)
