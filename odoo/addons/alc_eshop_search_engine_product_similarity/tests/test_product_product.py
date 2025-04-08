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

        product_model = ProductProduct.from_product_product(product)
        self.assertEqual(type(product_model.description_vector), str)
        self.assertEqual(type(product_model.characteristics_vector), str)
        self.assertEqual(
            [float(x) for x in product_model.description_vector.strip("[]").split(",")],
            product.description_vector.value.tolist(),
        )
        self.assertEqual(
            [
                float(x)
                for x in product_model.characteristics_vector.strip("[]").split(",")
            ],
            product.characteristics_vector.value.tolist(),
        )
