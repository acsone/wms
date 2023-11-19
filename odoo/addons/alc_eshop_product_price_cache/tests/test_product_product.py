# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import date, datetime, timedelta

from odoo import Command
from odoo.tests.common import TransactionCase

from odoo.addons.extendable.tests.common import ExtendableMixin
from odoo.addons.shopinvader_product.schemas.product import ProductProduct


class TestProductExpiryInSchema(TransactionCase, ExtendableMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.init_extendable_registry()
        cls.addClassCleanup(cls.reset_extendable_registry)

        cls.product = cls.env["product.product"].create(
            {"name": "test product", "lst_price": 100}
        )
        cls.model_pl = cls.env["product.pricelist"].with_context(
            queue_job__no_delay=True, ignore_es_update_role=True
        )

    def test_00(self):
        date_start = date.today()
        date_end = date.today() + timedelta(days=30)
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(product.price, {})
        pl = self.model_pl.create(
            {
                "name": "PL",
                "item_ids": [
                    Command.create(
                        {
                            "applied_on": "3_global",
                            "compute_price": "percentage",
                            "percent_price": 10,
                            "date_start": date_start,
                            "date_end": date_end,
                        }
                    )
                ],
            }
        )
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(len(product.price.get("price-pl")), 2)
        price = product.price.get("price-pl")[0]
        self.assertEqual(
            datetime.fromisoformat(price.get("date_start")).date(), date_start
        )
        self.assertEqual(datetime.fromisoformat(price.get("date_end")).date(), date_end)
        self.assertEqual(price.get("id"), pl.item_ids.id)
        self.assertEqual(price.get("price"), 90)

        price = product.price.get("price-pl")[1]
        self.assertIsNone(price.get("date_start"))
        self.assertIsNone(price.get("date_end"))
        self.assertIsNone(price.get("id"))
        self.assertEqual(price.get("price"), 100)
