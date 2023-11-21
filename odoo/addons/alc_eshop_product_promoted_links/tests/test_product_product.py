# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.tests.common import TransactionCase

from odoo.addons.extendable.tests.common import ExtendableMixin
from odoo.addons.shopinvader_product.schemas.product import ProductProduct


class TestProductSchema(TransactionCase, ExtendableMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.init_extendable_registry()
        cls.addClassCleanup(cls.reset_extendable_registry)
        cls.product = cls.env["product.product"].create({"name": "test product"})
        cls.product2 = cls.env["product.product"].create({"name": "test product 2"})
        cls.link_type = cls.env.ref("alc_product_promoted_links.link_type_promotes")

    def test_00(self):
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(product.cross, [])
        vals_link = {
            "right_product_tmpl_id": self.product.product_tmpl_id.id,
            "left_product_tmpl_id": self.product2.product_tmpl_id.id,
            "type_id": self.link_type.id,
        }
        # when
        self.env["product.template.link"].create(vals_link)
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(product.cross, [])
