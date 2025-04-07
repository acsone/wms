# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import TestProductSimilarityBase


class TestProductCharacteristic(TestProductSimilarityBase):
    def test_different_indices_for_same_attribute_with_different_name(self):
        dog_attribute_id = self.env.ref("alc_product_animal_species.dog").id
        product = self.env["product.product"].create(
            {
                "name": "Vitamines",
                "species_ids": [
                    (
                        6,
                        0,
                        [
                            dog_attribute_id,
                        ],
                    )
                ],
                "species_id": dog_attribute_id,
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "categ_id": self.env.ref(
                    "alc_product_category_data.product_categ_vitamines"
                ).id,
            }
        )
        indices_and_weights = self.env[
            "alc.product.characteristic"
        ].get_vector_indices_and_weights(
            product.species_ids, ["species_ids"]
        ) | self.env[
            "alc.product.characteristic"
        ].get_vector_indices_and_weights(
            product.species_id, ["specis_id"]
        )
        self.assertEqual(
            len(indices_and_weights),
            2,
            f"Attribute with id {dog_attribute_id} should appear twice. One for 'species_ids' and one for 'species_id'",
        )

    def test_get_vector_indices_on_empty_characteristics(self):
        self.assertEqual(
            {},
            self.env["alc.product.characteristic"].get_vector_indices_and_weights(
                self.product_material.species_ids,
                ["species_ids" for _ in range(len(self.product_material.species_ids))],
            ),
        )

    def test_vector_indices_remain_constant(self):
        first_indices = self.env[
            "alc.product.characteristic"
        ].get_vector_indices_and_weights(
            self.product_vitamines.species_ids,
            ["species_ids" for _ in range(len(self.product_vitamines.species_ids))],
        )
        second_indices = self.env[
            "alc.product.characteristic"
        ].get_vector_indices_and_weights(
            self.product_vitamines.species_ids,
            ["species_ids" for _ in range(len(self.product_vitamines.species_ids))],
        )
        self.assertEqual(first_indices, second_indices)

    def test_vector_indices_fit_holes(self):
        """Tests that vector indices vacated by deleted entries are reused before assigning new, larger indices."""

        # Delet indices in the middle
        to_delete_indices = {3, 5}
        for to_delete_index in to_delete_indices:
            to_delete_record = self.env["alc.product.characteristic"].search(
                [("vector_index", "=", to_delete_index)]
            )
            to_delete_record.unlink()

        new_product = self.env["product.product"].create(
            {
                "name": "Vitamines",
                "species_ids": [
                    (
                        6,
                        0,
                        [
                            self.env.ref("alc_product_animal_species.rat").id,
                            self.env.ref("alc_product_animal_species.reptile").id,
                            self.env.ref("alc_product_animal_species.rabbit").id,
                        ],
                    )
                ],
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "categ_id": self.env.ref(
                    "alc_product_category_data.product_categ_vitamines"
                ).id,
            }
        )

        # Ask for new indices (try to see if the deleted indices are given)
        new_product_vector_indices_and_weights = self.env[
            "alc.product.characteristic"
        ].get_vector_indices_and_weights(
            new_product.species_ids,
            ["species_ids" for _ in range(len(new_product.species_ids))],
        )

        self.assertEqual(
            {i for i, w in new_product_vector_indices_and_weights.values()}
            & to_delete_indices,
            to_delete_indices,
            f"Empty indices left over after deletion. New indices: { {i for i, w in new_product_vector_indices_and_weights.values()} } | deleted indices: {to_delete_indices}",
        )

    def test_number_characteristics_updates_species(self):
        nb_characteristics_0 = self.env[
            "alc.product.characteristic"
        ].get_number_indexed_characteristics()

        self.product_vitamines.species_ids[0].unlink()
        nb_characteristics_1 = self.env[
            "alc.product.characteristic"
        ].get_number_indexed_characteristics()

        test_species_1 = self.env["animal.species"].create(
            {"name": "Test animal species"}
        )
        test_species_2 = self.env["animal.species"].create(
            {"name": "Test animal species 2"}
        )
        # create a product using the new characteristics otherwise they won't be indexed
        self.env["product.product"].create(
            {
                "name": "Test",
                "species_ids": [
                    (
                        6,
                        0,
                        [test_species_1.id, test_species_2.id],
                    )
                ],
                "species_id": self.env.ref("alc_product_animal_species.all").id,
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "categ_id": self.env.ref(
                    "alc_product_category_data.product_categ_vitamines"
                ).id,
            }
        )
        self.env.flush_all()
        nb_characteristics_2 = self.env[
            "alc.product.characteristic"
        ].get_number_indexed_characteristics()

        self.assertEqual(
            nb_characteristics_0 - 1,
            nb_characteristics_1,
            "Number of indexed characteristics not properly indexed after deleting a species.",
        )
        self.assertEqual(
            nb_characteristics_0 + 1,
            nb_characteristics_2,
            "Number of indexed characteristics not properly indexed after addind species.",
        )

    def test_number_characteristics_updates_attribute(self):
        nb_characteristics_0 = self.env[
            "alc.product.characteristic"
        ].get_number_indexed_characteristics()

        self.product_vitamines.active_principle_option_ids[0].unlink()
        nb_characteristics_1 = self.env[
            "alc.product.characteristic"
        ].get_number_indexed_characteristics()

        test_attribute_1 = self.env["attribute.option"].create(
            {"name": "Test attribute", "attribute_id": 1}
        )
        test_attribute_2 = self.env["attribute.option"].create(
            {"name": "Test attribute 2", "attribute_id": 1}
        )
        # create a product using the new characteristics otherwise they won't be indexed
        self.env["product.product"].create(
            {
                "name": "Test",
                "species_id": self.env.ref("alc_product_animal_species.all").id,
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "categ_id": self.env.ref(
                    "alc_product_category_data.product_categ_vitamines"
                ).id,
                "active_principle_option_ids": [
                    (
                        6,
                        0,
                        [test_attribute_1.id, test_attribute_2.id],
                    )
                ],
            }
        )
        self.env.flush_all()
        nb_characteristics_2 = self.env[
            "alc.product.characteristic"
        ].get_number_indexed_characteristics()

        self.assertEqual(
            nb_characteristics_0 - 1,
            nb_characteristics_1,
            "Number of indexed characteristics not properly indexed after deleting an attribute.",
        )
        self.assertEqual(
            nb_characteristics_0 + 1,
            nb_characteristics_2,
            "Number of indexed characteristics not properly indexed after addind attributes.",
        )

    def test_number_characteristics_updates_category(self):
        nb_characteristics_0 = self.env[
            "alc.product.characteristic"
        ].get_number_indexed_characteristics()

        self.product_vitamines.categ_ids[-1].unlink()
        nb_characteristics_1 = self.env[
            "alc.product.characteristic"
        ].get_number_indexed_characteristics()

        test_category_1 = self.env["product.category"].create({"name": "Test category"})
        test_category_2 = self.env["product.category"].create(
            {"name": "Test category 2"}
        )
        # create a product using the new characteristics otherwise they won't be indexed
        self.env["product.product"].create(
            {
                "name": "Test",
                "species_id": self.env.ref("alc_product_animal_species.all").id,
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "categ_id": self.env.ref(
                    "alc_product_category_data.product_categ_vitamines"
                ).id,
                "categ_ids": [
                    (
                        6,
                        0,
                        [test_category_1.id, test_category_2.id],
                    )
                ],
            }
        )
        self.env.flush_all()
        nb_characteristics_2 = self.env[
            "alc.product.characteristic"
        ].get_number_indexed_characteristics()

        self.assertEqual(
            nb_characteristics_0 - 1,
            nb_characteristics_1,
            "Number of indexed characteristics not properly indexed after deleting a category.",
        )
        self.assertEqual(
            nb_characteristics_0 + 1,
            nb_characteristics_2,
            "Number of indexed characteristics not properly indexed after addind categories.",
        )
