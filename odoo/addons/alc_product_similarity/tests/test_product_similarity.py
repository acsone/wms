from unittest.mock import patch

from odoo.fields import Command
from odoo.tests.common import TransactionCase


class TestProductSimilarity(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category_a = cls.env["product.category"].create({"name": "Category A"})
        cls.category_b = cls.env["product.category"].create({"name": "Category B"})
        meds_category = cls.env.ref("alc_product_category_data.product_categ_medoc")

        cls.product_a = cls.env["product.product"].create(
            {
                "name": "Test Product A",
                "categ_ids": [Command.set([cls.category_a.id])],
                "categ_id": meds_category.id,
            }
        )
        cls.product_b = cls.env["product.product"].create(
            {
                "name": "Test Product B",
                "categ_ids": [Command.set([cls.category_a.id])],
            }
        )

    def test_01_compute_on_new_record_does_not_crash(self):
        new_product = self.env["product.product"].new({"name": "A Brand New Product"})
        self.assertFalse(
            new_product.similar_products_ids,
            "A new, unsaved record should have no similar products.",
        )

    def test_02_onchange_on_existing_record_keeps_value(self):
        # We use a "meds" product to ensure the characteristics vector is not empty
        # (chosen characteristics depend on the category of the product)
        self.assertTrue(self.product_a.is_meds)

        mock_path = "odoo.addons.alc_product_similarity.models.product_product.ProductProduct.get_similar_products"
        mock_return_value = [
            {"product": self.product_b},
        ]

        with patch(mock_path, return_value=mock_return_value) as mock_get_similar:
            self.product_a.flush_recordset()
            self.assertEqual(self.product_a.similar_products_ids, self.product_b)
            mock_get_similar.assert_called_once()
            mock_get_similar.reset_mock()

            # We create an in-memory record based on the original data.
            # This is our "virtual record" to simulates what happens on the client side
            original_data = self.product_a.copy_data()[0]
            virtual_product = self.env["product.product"].new(
                original_data, origin=self.product_a
            )

            # Now, we apply the user's change directly to the virtual record so as to
            # simulate what happens during a user interaction with odoo's web UI
            virtual_product.categ_ids = self.category_b
            self.assertNotEqual(
                virtual_product.characteristics_vector,
                virtual_product._origin.characteristics_vector,
                "The virtual product should have a different characteristics vector "
                "than its origin",
            )

            # We use ".ids" here because "virtual_product.similar_products_ids" is also made of
            # virtual products (with "type(id) = odoo.models.NewId")
            self.assertSetEqual(
                set(virtual_product.similar_products_ids.ids),
                set(self.product_b.ids),
                "The similar products list should not be cleared on a virtual record.",
            )
            mock_get_similar.assert_not_called()
