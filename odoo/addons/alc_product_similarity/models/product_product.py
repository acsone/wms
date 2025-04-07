# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from sentence_transformers import SentenceTransformer

from odoo import api, models

from odoo.addons.field_vector.fields import Vector


class ProductProduct(models.Model):
    _name = "product.product"
    _inherit = "product.product"

    _text_embedding_model = None  # lazy loading of the text embedding model

    characteristics_vector = Vector(
        string="Characteristics vector",
        readonly=True,
        compute="_compute_characteristics_vector",
        store=True,
        dimensions=1000,
    )
    description_vector = Vector(
        string="Description vector",
        readonly=True,
        compute="_compute_description_vector",
        store=True,
        dimensions=384,
    )

    @api.depends("name", "description_shop_long")
    def _compute_description_vector(self):
        """Computes the description_vector for the product."""
        for product in self:
            product.description_vector = product._get_description_vector()

    def _get_characteristics_infos(self):
        """
        Extracts the characteristics infos that will be used for similarity search (the extarcted characteristics are not the same depending on the type if the item).

        Returns:
            list[tuple]: a list of tuples of the form (<characteristic_record>, <characteristic_name>, <characteristic_weight>)
        """
        self.ensure_one()

        infos = []
        if self.is_meds:
            infos.extend([(x, "categ_ids", 1) for x in self.categ_ids])
            infos.extend(
                [
                    (x, "active_principle_option_ids", 2)
                    for x in self.active_principle_option_ids
                ]
            )
            infos.extend(
                [
                    (x, "administration_route_option_ids", 1)
                    for x in self.administration_route_option_ids
                ]
            )

        infos.extend([(x, "species_ids", 1) for x in self.species_ids])
        infos.extend([(x, "species_id", 1) for x in self.species_id])

        if self.is_food:
            infos.extend(
                [(x, "food_range_option_id", 1) for x in self.food_range_option_id]
            )
            infos.extend(
                [(x, "animal_size_option_ids", 1) for x in self.animal_size_option_ids]
            )
            infos.extend(
                [(x, "categ_age_option_ids", 1) for x in self.categ_age_option_ids]
            )
            infos.extend(
                [(x, "indication_option_ids", 1) for x in self.indication_option_ids]
            )
            infos.extend(
                [(x, "presentation_option_id", 1) for x in self.presentation_option_id]
            )

        if self.is_equipment:
            infos.extend([(x, "thread_option_id", 1) for x in self.thread_option_id])

        return infos

    def _get_characteristics_vector_dim(self):
        """Retrieves the characteristics vector dimension from system parameters."""
        param = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("alc_product_similarity.total_characteristics_dim")
        )

        if param:
            return int(param)
        default_dim = 1000
        self.env["ir.config_parameter"].sudo().set_param(
            "alc_product_similarity.total_characteristics_dim", str(default_dim)
        )
        return default_dim

    def _set_characteristics_vector_dim(self, dim):
        """Sets the characteristics vector dimension in system parameters."""
        self.env["ir.config_parameter"].sudo().set_param(
            "alc_product_similarity.total_characteristics_dim", str(dim)
        )

    @api.depends(
        "species_ids",
        "animal_size_option_ids",
        "categ_age_option_ids",
        "food_range_option_id",
        "indication_option_ids",
        "presentation_option_id",
        "active_principle_option_ids",
        "administration_route_option_ids",
        "categ_ids",
    )
    def _compute_characteristics_vector(self):
        """Computes the characteristic vector and updates the record in place."""
        vector_dim = self._get_characteristics_vector_dim()

        for product in self:
            characteristics_infos = product._get_characteristics_infos()
            vector_indices_and_weights = self.env[
                "alc.product.characteristic"
            ].get_vector_indices_and_weights(
                [infos[0] for infos in characteristics_infos],
                [infos[1] for infos in characteristics_infos],
                [infos[2] for infos in characteristics_infos],
            )

            number_indexed_characteristics = self.env[
                "alc.product.characteristic"
            ].get_number_indexed_characteristics()
            if number_indexed_characteristics > vector_dim:
                # TODO: update the dimension (and thus all vectors) here instead of throwing an error
                raise NotImplementedError(
                    "The total number of all possible characteristics exceeds the dimension of the characteristics vector. This case is not supported for now."
                )

            vector = [0 for _ in range(vector_dim)]
            for index, weight in vector_indices_and_weights.values():
                vector[index] = weight
            product.characteristics_vector = vector

    @api.model
    def _get_text_embedding_model(self):
        if not ProductProduct._text_embedding_model:
            ProductProduct._text_embedding_model = SentenceTransformer(
                "paraphrase-multilingual-MiniLM-L12-v2",
            )
        return ProductProduct._text_embedding_model

    def _get_description_vector(self):
        description = self.name + (
            ("\n" + str(self.description_shop_long))
            if self.description_shop_long
            else ""
        )

        return self._get_text_embedding_model().encode(
            description, show_progress_bar=False
        )

    def get_similar_products(self, limit):
        """
        Retrieves similar products based on vector distances.

        (Do not return this product in the the list)

        Args:
            limit (int): the maximum numer of similar prducts to return (limit parameter of the sql query).

        Returns:
            (list[dict]): a list of dicts of the form {
                'product': <product>,
                'characteristics_distance': <the characteristics vectors distance>,
                'description_distance': <the description vectors disance>,
            }
        """
        self.ensure_one()

        query = f"""
            SELECT
                id,
                pp.characteristics_vector <=> %s,
                pp.description_vector <=> %s
            FROM
                product_product AS pp
            WHERE
                pp.id != %s
            ORDER BY
                pp.characteristics_vector <=> %s,
                pp.description_vector <=> %s
            LIMIT {limit};
        """

        self.env.cr.execute(
            query,
            (
                self.characteristics_vector,
                self.description_vector,
                self.id,
                self.characteristics_vector,
                self.description_vector,
            ),
        )

        results = self.env.cr.fetchall()

        similar_products = []
        for row in results:
            product_id = row[0]
            product = self.browse(product_id)
            similar_products.append(
                {
                    "product": product,
                    "characteristics_distance": row[1],
                    "description_distance": row[2],
                }
            )

        return similar_products
