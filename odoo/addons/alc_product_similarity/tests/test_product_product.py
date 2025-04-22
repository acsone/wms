# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import json
from contextlib import contextmanager

import requests_mock

from .common import TestProductSimilarityBase


class TestProductProduct(TestProductSimilarityBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                queue_job__no_delay=True,
            )
        )
        cls.env["ir.config_parameter"].set_param(
            "alc_product_similarity_settings.product_description_vectorization_enabled",
            True,
        )
        cls.embed_service_url = "http://localhost:5000"
        cls.env["ir.config_parameter"].set_param(
            "alc_product_similarity_settings.embed_service_url",
            cls.embed_service_url,
        )
        cls.product_test_food = cls.product_test_food.with_env(cls.env)
        cls.product_material = cls.product_material.with_env(cls.env)
        cls.product_vitamines = cls.product_vitamines.with_env(cls.env)

    @contextmanager
    def mock_embed_service(self):
        with requests_mock.Mocker() as m:

            def call_back(request, context):
                rqst = json.loads(request.text)
                context.status_code = 200
                context.headers["Content-Type"] = "application/json"
                return {"embeddings": [[ord(c) for c in t] for t in rqst["texts"]]}

            m.post(
                f"{self.embed_service_url}/embed/products",
                json=call_back,
            )
            yield m

    def test_characteristics_vector_updates(self):
        characteristics_vector_0 = self.product_test_food.characteristics_vector
        self.product_test_food.write(
            {"species_ids": [(4, self.env.ref("alc_product_animal_species.horse").id)]}
        )
        characteristics_vector_1 = self.product_test_food.characteristics_vector
        self.product_test_food.write({"species_ids": [(5, 0, 0)]})
        characteristics_vector_2 = self.product_test_food.characteristics_vector

        non_zero_count_0 = sum(1 if x else 0 for x in characteristics_vector_0.value)
        non_zero_count_1 = sum(1 if x else 0 for x in characteristics_vector_1.value)
        non_zero_count_2 = sum(1 if x else 0 for x in characteristics_vector_2.value)
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
        with self.mock_embed_service():
            product_0 = self.env["product.product"].create(
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
                                self.env.ref("alc_product_animal_species.rat").id,
                                self.env.ref("alc_product_animal_species.reptile").id,
                                self.env.ref("alc_product_animal_species.sheep").id,
                            ],
                        )
                    ],
                }
            )
            product_1 = self.env["product.product"].create(
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
                                self.env.ref("alc_product_animal_species.rat").id,
                                self.env.ref("alc_product_animal_species.reptile").id,
                                self.env.ref("alc_product_animal_species.sheep").id,
                            ],
                        )
                    ],
                }
            )
            product_2 = self.env["product.product"].create(
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
                                self.env.ref("alc_product_animal_species.rat").id,
                                self.env.ref("alc_product_animal_species.reptile").id,
                            ],
                        )
                    ],
                }
            )
            self.env.flush_all()
            product_0_neighbors = [
                x["product"] for x in product_0.get_similar_products(limit=20)
            ]
            self.assertEqual(
                product_0_neighbors[0], product_1, "Unexpected first neighbor."
            )
            self.assertEqual(
                product_0_neighbors[1], product_2, "Unexpected second neighbor."
            )

    def test_description_vector_updates(self):
        with self.mock_embed_service() as m:
            self.product_test_food.description_sale_short = (
                "This is a short description"
            )
            self.assertTrue(m.called)

        with self.mock_embed_service() as m:
            self.product_test_food.product_tmpl_id.description_sale_long = (
                "This is a long description"
            )
            self.assertTrue(m.called)
