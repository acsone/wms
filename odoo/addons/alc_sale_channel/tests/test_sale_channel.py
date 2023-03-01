# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSaleChannel(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "partner"})
        cls.channel = cls.env["sale.channel"].create({"name": "channel"})
        cls.team = cls.env["crm.team"].create(
            {"name": "team", "sale_channel_id": cls.channel.id}
        )
        cls.sale_order = cls.env["sale.order"].create({"partner_id": cls.partner.id})

    def test_channel_at_team_change(self):
        self.assertFalse(self.sale_order.sale_channel_id)
        self.sale_order.team_id = self.team
        self.assertEqual(self.sale_order.sale_channel_id, self.channel)
