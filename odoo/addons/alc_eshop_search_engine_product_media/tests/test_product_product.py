# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.addons.shopinvader_product.schemas.product import ProductProduct
from odoo.addons.shopinvader_search_engine_product_media.tests.common import (
    ProductMediaCase,
)


class TestProductExpiryInSchema(ProductMediaCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.init_extendable_registry()
        cls.addClassCleanup(cls.reset_extendable_registry)
        cls.product = cls.product_a.with_context(index_id=cls.product_index.id)

    def test_00(self):
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(product.medias, [])

    def test_01(self):
        self.env["fs.product.media"].create(
            {
                "product_tmpl_id": self.product_a.product_tmpl_id.id,
                "media_id": self.media_c.id,
                "sequence": 10,
                "link_existing": True,
            }
        )
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(len(product.medias), 1)
        media = product.medias[0]
        self.assertIsNone(media.lang)

    def test_02(self):
        self.media_c.lang = "en_US"
        self.env["fs.product.media"].create(
            {
                "product_tmpl_id": self.product_a.product_tmpl_id.id,
                "media_id": self.media_c.id,
                "sequence": 10,
                "link_existing": True,
            }
        )
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(len(product.medias), 1)
        media = product.medias[0]
        self.assertEqual(media.lang, "en_US")
