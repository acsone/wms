# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
import io
import tempfile

from PIL import Image

from odoo.tests.common import TransactionCase

from odoo.addons.extendable.tests.common import ExtendableMixin
from odoo.addons.shopinvader_product.schemas.product import ProductProduct


class TestProductExpiryInSchema(TransactionCase, ExtendableMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.init_extendable_registry()
        cls.addClassCleanup(cls.reset_extendable_registry)

        temp_dir = tempfile.mkdtemp()
        cls.temp_backend = cls.env["fs.storage"].create(
            {
                "name": "Temp FS Storage",
                "protocol": "file",
                "code": "tmp_dir",
                "directory_path": temp_dir,
                "base_url": "http://my.public.files/",
            }
        )

        cls.brand = cls.env["product.brand"].create({"name": "brand"})
        cls.product = cls.env["product.product"].create(
            {"name": "product", "product_brand_id": cls.brand.id}
        )
        cls.image = cls._create_image(32, 32, color="#FFFFFF")
        cls.brand_image_model = cls.env["fs.product.brand.image"].with_context(
            storage_location=cls.temp_backend.code
        )

    @classmethod
    def _create_image(cls, width, height, color="#4169E1", img_format="PNG"):
        f = io.BytesIO()
        Image.new("RGB", (width, height), color).save(f, img_format)
        f.seek(0)
        return f.read()

    def test_00(self):
        product = ProductProduct.from_product_product(self.product)
        self.assertIsNone(product.brand.image_url)
        self.brand_image = self.brand_image_model.create(
            {
                "sequence": 1,
                "brand_id": self.brand.id,
                "specific_image": {
                    "filename": "image.png",
                    "content": base64.b64encode(self.image),
                },
            }
        )
        product = ProductProduct.from_product_product(self.product)
        self.assertEqual(
            product.brand.image_url,
            f"http://my.public.files/image-{self.brand.image._attachment.id}-0.png",
        )
