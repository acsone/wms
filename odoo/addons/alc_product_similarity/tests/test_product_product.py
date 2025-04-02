# Copyright 2025 Acsone
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon


class TestProductProduct(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.product_product = cls.env["product.product"]

    def test_1(self):
        product = self.product_product.create(
            {
                "name": "Test product",
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "categ_id": self.env.ref(
                    "alc_product_category_data.product_categ_undefined"
                ).id,
                "description_shop_long": "This is a long shop description",
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
        product._get_characteristics_vector_dim()
        # product.characteristics_vector
        # description_vector = product.description_vector
