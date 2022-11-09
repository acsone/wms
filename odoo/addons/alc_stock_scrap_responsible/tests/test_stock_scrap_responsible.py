# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestStockScrapResponsible(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(cls.env.context, tracking_disable=True, no_reset_password=True)
        )

    def test_stock_scrap_default_responsible(self):
        scrap = self.env["stock.scrap"].create(
            {
                "product_id": self.env.ref("product.product_product_4").id,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                "scrap_qty": 5.0,
                "location_id": self.env.ref("stock.stock_location_14").id,
            }
        )
        self.assertEqual(scrap.user_id, self.env.user)

    def test_stock_scrap_responsible(self):
        user = self.env["res.users"].create(
            {"name": "Test User", "login": "test_user", "email": "test.mail"}
        )
        scrap = self.env["stock.scrap"].create(
            {
                "product_id": self.env.ref("product.product_product_4").id,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                "scrap_qty": 5.0,
                "location_id": self.env.ref("stock.stock_location_14").id,
                "user_id": user.id,
            }
        )
        self.assertEqual(scrap.user_id, user)
