# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class PricelistDiscountCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = cls.env.ref("product.product_category_5")
        cls.supplier = cls.env.ref("base.res_partner_12")
        cls.sinfo = cls.env["product.supplierinfo"].create(
            {"partner_id": cls.supplier.id, "discount_sale": 10}
        )
        cls.product = cls.env["product.product"].create({"name": "Unittest P1"})
        cls.sinfo_model = cls.env["product.supplierinfo"]

    def test_check_dates(self):
        """Test exceptions with promotion dates."""

        self.sinfo_model.search(
            [("product_tmpl_id", "=", self.product.product_tmpl_id.id)]
        ).unlink()

        # Create the default price
        self.sinfo_model.create(
            {
                "partner_id": self.supplier.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
            }
        )

        # Test to create a new default price
        with self.assertRaises(ValidationError):
            self.sinfo_model.create(
                {
                    "partner_id": self.supplier.id,
                    "product_tmpl_id": self.product.product_tmpl_id.id,
                }
            )

        # Test to create a promo without end date
        with self.assertRaises(ValidationError):
            self.sinfo_model.create(
                {
                    "partner_id": self.supplier.id,
                    "product_tmpl_id": self.product.product_tmpl_id.id,
                    "date_start": "2018-01-01",
                }
            )

        # Test to create a promo without start date
        with self.assertRaises(ValidationError):
            self.sinfo_model.create(
                {
                    "partner_id": self.supplier.id,
                    "product_tmpl_id": self.product.product_tmpl_id.id,
                    "date_end": "2018-01-01",
                }
            )

        # Promo 1 (2018-01-01 -> 2018-03-31)
        self.sinfo_model.create(
            {
                "partner_id": self.supplier.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "date_start": "2018-01-01",
                "date_end": "2018-03-31",
                "discount_sale": 10,
                "discount_purchase": 15,
            }
        )

        # Promo 3 (2018-08-01 -> 2018-12-31)
        self.sinfo_model.create(
            {
                "partner_id": self.supplier.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "date_start": "2018-08-01",
                "date_end": "2018-12-31",
                "discount_sale": 10,
                "discount_purchase": 15,
            }
        )

        # Promo 2 (2018-04-01 -> 2018-06-30)
        self.sinfo_model.create(
            {
                "partner_id": self.supplier.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "date_start": "2018-04-01",
                "date_end": "2018-06-30",
                "discount_sale": 10,
                "discount_purchase": 15,
            }
        )

        # Test overlaps (2018-12-01 -> 2019-03-01) blocked by the promo 3
        # (2018-08-01 -> 2018-12-31)
        with self.assertRaises(ValidationError):
            self.sinfo_model.create(
                {
                    "partner_id": self.supplier.id,
                    "product_tmpl_id": self.product.product_tmpl_id.id,
                    "date_start": "2018-12-01",
                    "date_end": "2019-03-01",
                }
            )

        # Test overlaps (2018-03-01 -> 2018-06-01) blocked by the promo 1
        # (2018-01-01 -> 2018-03-31) and 2 (2018-04-01 -> 2018-06-30)
        with self.assertRaises(ValidationError):
            self.sinfo_model.create(
                {
                    "partner_id": self.supplier.id,
                    "product_tmpl_id": self.product.product_tmpl_id.id,
                    "date_start": "2018-03-01",
                    "date_end": "2018-06-01",
                }
            )

        # Test inverse date_start and date_end
        with self.assertRaises(ValidationError):
            self.sinfo_model.create(
                {
                    "partner_id": self.supplier.id,
                    "product_tmpl_id": self.product.product_tmpl_id.id,
                    "date_start": "2017-12-31",
                    "date_end": "2017-01-01",
                }
            )

        # Test overlaps with different min_qty
        # Promo 1 (2018-01-01 -> 2018-03-31) with min_qty == 100
        self.sinfo_model.create(
            {
                "partner_id": self.supplier.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "date_start": "2018-01-01",
                "date_end": "2018-03-31",
                "min_qty": 100,
                "discount_sale": 10,
                "discount_purchase": 20,
            }
        )

        # Test overlaps with different min_qty_sale
        # Promo 2 (2018-04-01 -> 2018-06-30) with min_qty_sale == 25
        self.sinfo_model.create(
            {
                "partner_id": self.supplier.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "date_start": "2018-04-01",
                "date_end": "2018-06-30",
                "min_qty_sale": 25,
                "discount_sale": 11.5,
                "discount_purchase": 15,
            }
        )

        # Test overlaps with different min_qty_sale
        # Promo 2 (2018-04-01 -> 2018-06-30) with min_qty_sale == 50
        self.sinfo_model.create(
            {
                "partner_id": self.supplier.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "date_start": "2018-04-01",
                "date_end": "2018-06-30",
                "min_qty_sale": 50,
                "discount_sale": 14,
                "discount_purchase": 15,
            }
        )

        # Test overlaps with the same min_qty and min_qty_sale
        with self.assertRaises(ValidationError):
            self.sinfo_model.create(
                {
                    "partner_id": self.supplier.id,
                    "product_tmpl_id": self.product.product_tmpl_id.id,
                    "date_start": "2018-04-01",
                    "date_end": "2018-06-30",
                    "min_qty_sale": 50,
                    "discount_sale": 14,
                    "discount_purchase": 15,
                }
            )

    def test_product_supplierinfo_order(self):
        self.sinfo_model.search(
            [("product_tmpl_id", "=", self.product.product_tmpl_id.id)]
        ).unlink()

        # Create the default price
        self.sinfo_model.create(
            {
                "partner_id": self.supplier.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
            }
        )
        self.sinfo_model.create(
            {
                "partner_id": self.supplier.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "date_start": "2018-04-01",
                "date_end": "2018-06-30",
                "min_qty_sale": 50,
                "discount_sale": 14,
                "discount_purchase": 15,
            }
        )
        records = self.sinfo_model.search([])
        self.assertTrue(records[0].date_start)
        self.assertFalse(records[1].date_start)
