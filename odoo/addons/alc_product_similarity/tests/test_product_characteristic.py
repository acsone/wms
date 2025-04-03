# Copyright 2025 Acsone
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon


class TestProductCharacteristic(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.product_vitamines = cls.env["product.product"].create(
            {
                "name": "Vitamines",
                "species_ids": [
                    (
                        6,
                        0,
                        [
                            cls.env.ref("alc_product_animal_species.dog").id,
                            cls.env.ref("alc_product_animal_species.cat").id,
                            cls.env.ref("alc_product_animal_species.ferret").id,
                            cls.env.ref("alc_product_animal_species.bee").id,
                            cls.env.ref("alc_product_animal_species.cattle").id,
                            cls.env.ref("alc_product_animal_species.chinchilla").id,
                            cls.env.ref("alc_product_animal_species.horse").id,
                            cls.env.ref("alc_product_animal_species.mouse").id,
                            cls.env.ref("alc_product_animal_species.pigeon").id,
                            cls.env.ref("alc_product_animal_species.pig").id,
                        ],
                    )
                ],
                "species_id": cls.env.ref("alc_product_animal_species.all").id,
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "categ_id": cls.env.ref(
                    "alc_product_category_data.product_categ_vitamines"
                ).id,
            }
        )

        cls.product_material = cls.env["product.product"].create(
            {
                "name": "Important material",
                "categ_id": cls.env.ref(
                    "alc_product_category_data.product_categ_materiel"
                ).id,
            }
        )

        cls.product_characteric = cls.env["alc.product.characteristic"]

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
        indices_and_weights = self.product_characteric.get_vector_indices_and_weights(
            product.species_ids, ["species_ids"]
        ) | self.product_characteric.get_vector_indices_and_weights(
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
            self.product_characteric.get_vector_indices_and_weights(
                self.product_material.species_ids,
                ["species_ids" for _ in range(len(self.product_material.species_ids))],
            ),
        )

    def test_vector_indices_remain_constant(self):
        first_indices = self.product_characteric.get_vector_indices_and_weights(
            self.product_vitamines.species_ids,
            ["species_ids" for _ in range(len(self.product_vitamines.species_ids))],
        )
        second_indices = self.product_characteric.get_vector_indices_and_weights(
            self.product_vitamines.species_ids,
            ["species_ids" for _ in range(len(self.product_vitamines.species_ids))],
        )
        self.assertEqual(first_indices, second_indices)

    def test_vector_indices_fit_holes(self):
        """Tests that vector indices vacated by deleted entries are reused before assigning new, larger indices."""

        # Delet indices in the middle
        to_delete_indices = {3, 5}
        for to_delete_index in to_delete_indices:
            to_delete_record = self.product_characteric.search(
                [("vector_index", "=", to_delete_index)]
            )
            to_delete_record.unlink()

        self.env["product.product"].create(
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
        new_product_vector_indices_and_weights = (
            self.product_characteric.get_vector_indices_and_weights(
                self.product_vitamines.species_ids,
                ["species_ids" for _ in range(len(self.product_vitamines.species_ids))],
            )
        )

        self.assertEqual(
            {i for i, w in new_product_vector_indices_and_weights.values()}
            & to_delete_indices,
            to_delete_indices,
            f"Empty indices left over after deletion. New indices: { {i for i, w in new_product_vector_indices_and_weights.values()} } | deleted indices: {to_delete_indices}",
        )
