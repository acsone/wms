# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.connector_search_engine.tests.test_all import TestBindingIndexBaseFake


class TestProductAutoBind(TestBindingIndexBaseFake):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.product_obj = cls.env["product.product"]
        cls.backend.product_assortment_id = cls.env.ref(
            "shopinvader_search_engine_assortment.shopinvader_assortment1"
        )
        cls.backend.product_manual_binding = False
        cls.backend.product_assortment_id.domain = "[('sale_ok', '=', True)]"
        cls.product_index = cls.env["se.index"].create(
            {
                "name": "product",
                "backend_id": cls.backend.id,
                "model_id": cls.env.ref("product.model_product_product").id,
                "serializer_type": "shopinvader_product_exports",
            }
        )
        cls.product_template_in = cls.env["product.template"].create({"name": "P"})
        cls.product_in = cls.product_template_in.product_variant_id

        cls.product_template_out = cls.env["product.template"].create({"name": "N"})
        cls.product_out = cls.product_template_out.product_variant_id

        cls.product_templates = cls.product_template_in + cls.product_template_out
        cls.products = cls.product_in + cls.product_out
        vals_assortment = {
            "domain": "[('name', '=', 'P')]",
            "model_id": "product.product",
            "name": "assortment",
        }
        cls.assortment = cls.env["ir.filters"].create(vals_assortment)
        cls.backend.product_assortment_id = cls.assortment

    def test_template(self):
        self.assertFalse(self.product_index.binding_ids)
        self.product_templates.shopinvader_assortment_binding()
        self.assertEqual(self.product_in, self.product_index.binding_ids.record)

    def test_product(self):
        self.assertFalse(self.product_index.binding_ids)
        self.products.shopinvader_assortment_binding()
        self.assertEqual(self.product_in, self.product_index.binding_ids.record)

    def test_unbind_product(self):
        # given
        product_out_binding = self.product_out._add_to_index(self.product_index)
        self.assertEqual(self.product_out, self.product_index.binding_ids.record)
        # when
        self.products.shopinvader_assortment_binding()
        # then
        self.assertEqual(product_out_binding.state, "to_delete")
