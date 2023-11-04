# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSaleChannel(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})

    def test_create(self):
        cart = self.env["sale.order"]._create_empty_cart(self.partner.id)
        self.assertEqual(
            cart.sale_channel_id,
            self.env.ref("alc_sale_channel.sale_channel_web"),
        )
        self.assertEqual(
            cart.team_id, self.env.ref("sales_team.salesteam_website_sales")
        )
