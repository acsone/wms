# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.addons.shopinvader_search_engine_update.tests.common import (
    TestProductBindingUpdateBase,
)


class TestProductExportFlow(TestProductBindingUpdateBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_template = cls.product.product_tmpl_id

    def test_0(self):
        # create case
        self.assertEqual(self.product_binding.state, "done")
        vals = {"product_template_id": self.product_template.id}
        special = self.env["product.discount.special"].create(vals)
        self.assertEqual(self.product_binding.state, "to_recompute")
        # write case
        self.product_binding.state = "done"
        special.date_start = "2023-01-01"
        self.assertEqual(self.product_binding.state, "to_recompute")
        # unlink case
        self.product_binding.state = "done"
        special.unlink()
        self.assertEqual(self.product_binding.state, "to_recompute")
