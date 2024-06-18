# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import date, timedelta

from odoo import Command
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger

from odoo.addons.extendable.tests.common import ExtendableMixin
from odoo.addons.shopinvader_product.schemas.product import ProductProduct


class TestProductSchema(TransactionCase, ExtendableMixin):
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

    @mute_logger("odoo.addons.queue_job.utils")
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
        prices = product.price.get(pl.role_name)
        self.assertEqual(len(prices), 2)
        price = list(filter(lambda p, i=pl.item_ids: p.id == i.id, prices))[0]
        self.assertEqual(price.date_start, date_start)
        self.assertEqual(price.date_end, date_end)
        self.assertEqual(price.id, pl.item_ids.id)
        self.assertEqual(price.price, 90)
        self.assertEqual(price.exclusive, False)

        price = list(filter(lambda p, i=pl.item_ids: p.id != i.id, prices))[0]
        self.assertIsNone(price.date_start)
        self.assertIsNone(price.date_end)
        self.assertIsNone(price.id)
        self.assertEqual(price.price, 100)
        self.assertEqual(price.exclusive, False)
