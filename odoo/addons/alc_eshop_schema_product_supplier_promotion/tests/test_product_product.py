# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import date, timedelta

from odoo.tests.common import TransactionCase

from odoo.addons.extendable.tests.common import ExtendableMixin

from ..schemas import ProductProduct


class TestProductExpiryInSchema(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        ExtendableMixin.init_extendable_registry()

        @cls.addClassCleanup
        def cleanup():
            ExtendableMixin.reset_extendable_registry()

        cls.product = cls.env["product.product"].create(
            {"name": "test product", "tracking": "lot", "type": "product"}
        )
        cls.supplier = cls.env["res.partner"].create({"name": "Supplier"})

    def test_00(self):
        date_start = date.today().isoformat()
        date_end = (date.today() + timedelta(days=30)).isoformat()
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(product.supplier_promotion, [])
        self.env["product.supplierinfo"].create(
            {
                "partner_id": self.supplier.id,
                "product_code": "product_code",
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "ratio_main_product": 1,
                "ratio_promotional_product": 1,
                "date_start": date_start,
                "date_end": date_end,
            }
        )
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(len(product.supplier_promotion), 1)
        promotion = product.supplier_promotion[0]
        self.assertEqual(promotion.get("date_start"), date_start)
        self.assertEqual(promotion.get("date_end"), date_end)
        self.assertEqual(promotion.get("ratio_main_product"), 1)
        self.assertEqual(promotion.get("ratio_promotional_product"), 1)
        self.assertDictEqual(
            promotion.get("time_frame"), {"gte": date_start, "lte": date_end}
        )

    def test_01(self):
        date_start = date.today().isoformat()
        date_end = (date.today() + timedelta(days=30)).isoformat()
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(product.supplier_promotion_veterinary, [])
        self.env["product.supplierinfo"].create(
            {
                "partner_id": self.supplier.id,
                "product_code": "product_code",
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "ratio_main_product": 1,
                "ratio_promotional_product": 1,
                "date_start": date_start,
                "date_end": date_end,
                "only_for_veterinaries": True,
            }
        )
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(len(product.supplier_promotion_veterinary), 1)
        promotion = product.supplier_promotion_veterinary[0]
        self.assertEqual(promotion.get("date_start"), date_start)
        self.assertEqual(promotion.get("date_end"), date_end)
        self.assertEqual(promotion.get("ratio_main_product"), 1)
        self.assertEqual(promotion.get("ratio_promotional_product"), 1)
        self.assertDictEqual(
            promotion.get("time_frame"), {"gte": date_start, "lte": date_end}
        )

    def test_02(self):
        date_start = date.today().isoformat()
        date_end = (date.today() + timedelta(days=30)).isoformat()
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(product.supplier_discount, [])
        self.env["product.supplierinfo"].create(
            {
                "partner_id": self.supplier.id,
                "product_code": "product_code",
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "date_start": date_start,
                "date_end": date_end,
                "discount_sale": 10,
            }
        )
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(len(product.supplier_discount), 1)
        promotion = product.supplier_discount[0]
        self.assertEqual(promotion.get("date_start"), date_start)
        self.assertEqual(promotion.get("date_end"), date_end)
        self.assertEqual(promotion.get("discount_sale"), 10.0)
        self.assertDictEqual(
            promotion.get("time_frame"), {"gte": date_start, "lte": date_end}
        )
