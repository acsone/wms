# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64

from odoo.tests.common import TransactionCase

from odoo.addons.extendable.tests.common import ExtendableMixin
from odoo.addons.shopinvader_product.schemas.product import ProductProduct


class TestProductSchema(TransactionCase, ExtendableMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.init_extendable_registry()
        cls.addClassCleanup(cls.reset_extendable_registry)
        cls.product = cls.env["product.product"].create({"name": "Product"})
        cls.media_type = cls.env["fs.media.type"].create(
            {"name": "Media Type", "code": "media_type"}
        )
        cls.media = cls.env["fs.media"].create(
            {
                "file": {
                    "filename": "c.txt",
                    "content": base64.b64encode(b"media content c"),
                },
                "media_type_id": cls.media_type.id,
            }
        )

    def test_00(self):
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(product.medias, [])

    def test_01(self):
        self.env["fs.product.media"].create(
            {
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "media_id": self.media.id,
                "sequence": 10,
                "link_existing": True,
            }
        )
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(len(product.medias), 1)
        media = product.medias[0]
        self.assertIsNone(media.lang)

    def test_02(self):
        self.media.lang = "en_US"
        self.env["fs.product.media"].create(
            {
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "media_id": self.media.id,
                "sequence": 10,
                "link_existing": True,
            }
        )
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(len(product.medias), 1)
        media = product.medias[0]
        self.assertEqual(media.lang, "en_US")
