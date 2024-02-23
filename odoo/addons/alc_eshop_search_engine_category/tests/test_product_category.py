# Copyright 2017-2018 Akretion (http://www.akretion.com).
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.shopinvader_search_engine.tests.common import TestCategoryBindingBase


class TestCategory(TestCategoryBindingBase):
    def test_00(self):
        category = self.env["product.category"].create({"name": "category"})
        category._compute_binding_ids()
        self.assertFalse(category.se_binding_ids)
        category.shopinvader_category_bind()
        category._compute_binding_ids()
        self.assertTrue(category.se_binding_ids)
        binding = category.se_binding_ids.filtered(
            lambda b, i=self.se_categ_index: b.index_id == i
        )
        self.assertEqual(binding.state, "to_recompute")
        category.shopinvader_category_unbind()
        self.assertEqual(binding.state, "to_delete")
