# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestProductPackaging(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.packaging_pallette = cls.env.ref(
            "alc_product_packaging.product_packaging_type_palette"
        )
        cls.packaging_box = cls.env.ref(
            "alc_product_packaging.product_packaging_type_box"
        )
        cls.packaging_shrink = cls.env.ref(
            "alc_product_packaging.product_packaging_type_shrink_wrap"
        )

        cls.product = (
            cls.env["product.template"]
            .create({"name": "Product Test for packagings"})
            .product_variant_ids
        )

        cls.packaging_pallet = cls.env["product.packaging"].create(
            {
                "name": "Test pallet",
                "packaging_level_id": cls.packaging_pallette.id,
                "product_id": cls.product.id,
                "qty": 15.0,
            }
        )
        cls.packaging_box = cls.env["product.packaging"].create(
            {
                "name": "Test box",
                "packaging_level_id": cls.packaging_box.id,
                "product_id": cls.product.id,
                "qty": 5.0,
            }
        )
        cls.packaging_shrink = cls.env["product.packaging"].create(
            {
                "name": "Test shrink",
                "packaging_level_id": cls.packaging_shrink.id,
                "product_id": cls.product.id,
                "qty": 30.0,
            }
        )

    def test_product_packaging(self):
        self.assertEqual(self.product.unit_in_pallet, 15.0)

        self.assertEqual(self.product.unit_in_box, 5.0)

        self.assertEqual(self.product.unit_in_shrink_wrap, 30.0)
