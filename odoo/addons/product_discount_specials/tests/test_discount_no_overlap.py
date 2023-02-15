# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import SavepointCase


class TestDiscountNoOverlap(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestDiscountNoOverlap, cls).setUpClass()
        cls.product = cls.env["product.template"].create({"name": "product test"})

        cls.discount1 = cls.env["product.discount.special"].create(
            {
                "date_start": "2023-01-20",
                "date_end": "2023-01-30",
                "product_template_id": cls.product.id,
            }
        )

    def test_00_discount_end_before_start(self):
        with self.assertRaises(ValidationError):
            self.env["product.discount.special"].create(
                {
                    "date_start": "2023-02-25",
                    "date_end": "2023-02-20",
                    "product_template_id": self.product.id,
                }
            )

    def test_01_discount_overlaps_beginning_discount1(self):
        with self.assertRaises(ValidationError):
            self.env["product.discount.special"].create(
                {
                    "date_start": "2023-01-10",
                    "date_end": "2023-01-22",
                    "product_template_id": self.product.id,
                }
            )

    def test_02_discount_overlaps_end_discount1(self):
        with self.assertRaises(ValidationError):
            self.env["product.discount.special"].create(
                {
                    "date_start": "2023-01-25",
                    "date_end": "2023-02-01",
                    "product_template_id": self.product.id,
                }
            )

    def test_03_discount_before_discount1(self):
        discount2 = self.env["product.discount.special"].create(
            {
                "date_start": "2023-01-10",
                "date_end": "2023-01-19",
                "product_template_id": self.product.id,
            }
        )
        self.assertTrue(discount2)

    def test_04_discount_after_discount1(self):
        discount2 = self.env["product.discount.special"].create(
            {
                "date_start": "2023-02-01",
                "date_end": "2023-02-10",
                "product_template_id": self.product.id,
            }
        )
        self.assertTrue(discount2)

    def test_05_discount_starts_when_discount1_ends(self):
        with self.assertRaises(ValidationError):
            self.env["product.discount.special"].create(
                {
                    "date_start": "2023-01-30",
                    "date_end": "2023-02-06",
                    "product_template_id": self.product.id,
                }
            )

    def test_06_discount_ends_when_discount1_start(self):
        with self.assertRaises(ValidationError):
            self.env["product.discount.special"].create(
                {
                    "date_start": "2023-01-05",
                    "date_end": "2023-01-20",
                    "product_template_id": self.product.id,
                }
            )
