# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.alc_product_supplier.tests.common import TestProductTemplateCommon


class TestProductProduct(TestProductTemplateCommon):
    def test_name_search(self):
        """Test search by vendor code."""
        self.assertEqual(
            self.env["product.product"]
            .with_context(partner_id=self.supplier.id)
            .name_search("ABCD"),
            [(self.product_seller.product_variant_ids.id, "[ABCD] with seller")],
        )

    def test_name_search_vendor_product_code(self):
        """Test search by vendor code without context."""
        self.assertEqual(
            self.env["product.product"].name_search("ABCD"),
            [(self.product_seller.product_variant_ids.id, "[1234] with seller")],
        )
