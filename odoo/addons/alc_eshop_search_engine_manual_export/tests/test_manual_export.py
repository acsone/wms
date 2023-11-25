# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_search_engine.tests.common import TestProductBindingBase


class TestManualExport(TestProductBindingBase):
    def test_0(self):
        """Existing binding."""
        self.assertEqual(self.product_binding.state, "to_recompute")
        self.product.shopinvader_manual_export()
        self.assertEqual(self.product_binding.state, "done")

    def test_1(self):
        """New product, not bound yet."""
        products = self.env["product.product"].create(
            [{"name": "product 1"}, {"name": "product 2"}]
        )
        products.shopinvader_manual_export()
        bindings = products._get_bindings()
        self.assertTrue(bindings)
        self.assertEqual(bindings[0].state, "done")

    def test_2(self):
        """From product template."""
        self.assertEqual(self.product_binding.state, "to_recompute")
        self.product.product_tmpl_id.shopinvader_manual_export()
        self.assertEqual(self.product_binding.state, "done")
