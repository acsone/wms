# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon

from ..schemas.product_product import ProductProduct


class TestProductSimilarityBase(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_product_product_pydantic(self):
        product = self.env["product.product"].create(
            {
                "name": "Test product",
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "categ_id": self.env.ref(
                    "alc_product_category_data.product_categ_ali_divers"
                ).id,
                "description_shop_long": "This is a long shop description for this amazing product!!!",
                "species_ids": [
                    (
                        6,
                        0,
                        [
                            self.env.ref("alc_product_animal_species.dog").id,
                            self.env.ref("alc_product_animal_species.cat").id,
                            self.env.ref("alc_product_animal_species.ferret").id,
                        ],
                    )
                ],
            }
        )
        # we set random verctor values since the vector creation is disabled
        # in the test environment
        product.description_vector = [0.1, 0.2, 0.3]
        product.characteristics_vector = [0.4, 0.5, 0.6]

        product_model = ProductProduct.from_product_product(product)
        self.assertListEqual(
            product_model.description_vector,
            product.description_vector.to_list(),
        )
        self.assertListEqual(
            product_model.characteristics_vector,
            product.characteristics_vector.to_list(),
        )

        # the vectors are nullable
        product.description_vector = None
        product.characteristics_vector = None
        product_model = ProductProduct.from_product_product(product)
        self.assertIsNone(product_model.description_vector)
        self.assertIsNone(product_model.characteristics_vector)
