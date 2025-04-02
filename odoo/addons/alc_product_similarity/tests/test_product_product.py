# Copyright 2025 Acsone
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon


class TestProductProduct(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.product_product = cls.env["product.product"]
        cls.product = cls.product_product.create(
            {
                "name": "Test product",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "categ_id": cls.env.ref(
                    "alc_product_category_data.product_categ_undefined"
                ).id,
                "description_shop_long": "This is a long shop description",
                "species_ids": [
                    (
                        6,
                        0,
                        [
                            cls.env.ref("alc_product_animal_species.dog").id,
                            cls.env.ref("alc_product_animal_species.cat").id,
                            cls.env.ref("alc_product_animal_species.ferret").id,
                        ],
                    )
                ],
                "animal_size_option_ids": [
                    (
                        6,
                        0,
                        [
                            cls.env.ref(
                                "alc_pim.option_attribute_animal_size_small"
                            ).id,
                            cls.env.ref(
                                "alc_pim.option_attribute_animal_size_medium"
                            ).id,
                        ],
                    )
                ],
                "categ_age_option_ids": [
                    (
                        6,
                        0,
                        [
                            cls.env.ref("alc_pim.attribute_option_senior").id,
                            cls.env.ref("alc_pim.attribute_option_adult").id,
                        ],
                    )
                ],
                "food_range_option_id": cls.env.ref(
                    "alc_pim.attribute_option_recovery"
                ).id,
                "indication_option_ids": [
                    (
                        6,
                        0,
                        [
                            cls.env.ref("alc_pim.attribute_option_oral").id,
                            cls.env.ref("alc_pim.attribute_option_heart").id,
                        ],
                    )
                ],
                "presentation_option_id": cls.env.ref(
                    "alc_pim.attribute_option_croquette"
                ).id,
                "active_principle_option_ids": [
                    (
                        6,
                        0,
                        [
                            cls.env.ref("alc_pim.attribute_option_croquette").id,
                        ],
                    )
                ],
            }
        )

    def test_characteristics_vector_updates(self):
        characteristics_vector_0 = self.product.characteristics_vector
        self.product.write(
            {"species_ids": [(4, self.env.ref("alc_product_animal_species.horse").id)]}
        )
        characteristics_vector_1 = self.product.characteristics_vector
        self.product.write({"species_ids": [(5, 0, 0)]})
        characteristics_vector_2 = self.product.characteristics_vector

        non_zero_count_0 = characteristics_vector_0.count("1")
        non_zero_count_1 = characteristics_vector_1.count("1")
        non_zero_count_2 = characteristics_vector_2.count("1")
        self.assertEqual(
            non_zero_count_0 + 1,
            non_zero_count_1,
            f"Expected {non_zero_count_0 + 1} non zero entries after product update but found {non_zero_count_1}",
        )
        self.assertEqual(
            non_zero_count_0 - 3,
            non_zero_count_2,
            f"Expected {non_zero_count_0 - 3} non zero entries after product update but found {non_zero_count_2}",
        )

    def test_get_similar_products(self):
        product = self.product_product.create(
            {
                "name": "Another test product",
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
        product.get_similar_products(limit=20)

    # def test_description_vector(self):
    #     description_vector = self.product.description_vector
    #     pass
