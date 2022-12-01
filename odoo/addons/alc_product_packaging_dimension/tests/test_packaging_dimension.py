# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestPackagingDimension(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.cm_uom = cls.env.ref("uom.product_uom_cm")
        cls.mm_uom = cls.env.ref("uom.product_uom_millimeter")

        cls.packaging = cls.env["product.packaging"].create(
            {
                "name": "Product Packaging Test",
                "packaging_length": 300,
                "length_uom_id": cls.mm_uom.id,
                "width": 500,
                "height": 200,
            }
        )

    def test_packaging_displayed_dimensions(self):
        self.assertEqual("cm", self.packaging.displayed_uom_name)
        self.assertEqual(30, self.packaging.displayed_length)
        self.assertEqual(50, self.packaging.displayed_width)
        self.assertEqual(20, self.packaging.displayed_height)

        self.assertEqual(30.0, self.packaging.volume_l)
