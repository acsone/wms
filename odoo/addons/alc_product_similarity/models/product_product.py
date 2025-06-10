# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import os

import requests

from odoo import _, api, fields, models
from odoo.tools import str2bool
from odoo.tools.sql import create_index

from odoo.addons.field_vector.fields import Vector


class ProductProduct(models.Model):
    _name = "product.product"
    _inherit = "product.product"

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
        dimensions=384,
    )
    similar_products_ids = fields.Many2many(
        string="Similar products",
        comodel_name="product.product",
        readonly=True,
        store=False,
        compute="_compute_similar_products_ids",
    )

    def init(self):  # pylint: disable=missing-return
        create_index(
            self.env.cr,
            "product_product_characteristics_vector_index",
            self._table,
            ["characteristics_vector vector_cosine_ops"],
            method="hnsw",
        )
        create_index(
            self.env.cr,
            "product_product_description_vector_index",
            self._table,
            ["description_vector vector_cosine_ops"],
            method="hnsw",
        )
        super().init()

    @api.depends("description_vector", "characteristics_vector")
    def _compute_similar_products_ids(self):
        """
        This compute method is triggered in three main scenarios:

        1. On a brand new, unsaved record (a "NewId").
        2. When loading a saved record from the database.
        3. During an "onchange" on a saved record.

        The similarity search uses a DB index and MUST NOT run on virtual
        data from scenarios 1 or 3.

        We can detect scenarios 1 and 3 by checking if the record has a
        database-backed origin. A new record has no origin. An existing
        record in an onchange has an origin, but the in-memory values
        for its dependencies may have changed.

        A robust way to handle this is to check if the dependencies have changed
        from their original, saved state.
        """
        for product in self:

            if (
                not product._origin.id
                or (
                    product._origin.characteristics_vector
                    != product.characteristics_vector
                )
                or (product._origin.description_vector != product.description_vector)
            ):
                # CASE 1: This is a brand-new record (no origin).
                # CASE 2: The dependencies have changed in memory (onchange event).
                # In either case, a new search would fail.
                # To prevent the UI list from disappearing during an onchange,
                # we explicitly assign the value from the origin. For a new record,
                # this will correctly result in an empty list.
                product.similar_products_ids = product._origin.similar_products_ids
            else:
                similar_products_infos = product.get_similar_products(5)
                product.similar_products_ids = [
                    x["product"].id for x in similar_products_infos
                ]

    @api.model
    def _is_product_description_vectorization_enabled(self):
        return str2bool(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "alc_product_similarity_settings.product_description_vectorization_enabled"
            )
        )

    @property
    def embed_service_url(self):
        return self.env["ir.config_parameter"].sudo().get_param(
            "alc_product_similarity_settings.embed_service_url"
        ) or os.environ.get("EMBED_SERVER_URL")

    def _delay_compute_description_vector(self):
        """
        Triggers the computation of the description vector in the background.

        using a queue job.
        """
        if not self._is_product_description_vectorization_enabled():
            return
        for record in self:
            record.with_delay(
                description=_(
                    "Compute description vector for product %(name)s",
                    name=record.display_name,
                )
            )._compute_description_vector()

    def _get_description_vector_input_text(self):
        description = self.description_sale_long or self.description_sale_short
        return self.name + (("\n" + str(description)) if self.description else "")

    def _compute_description_vector(self):
        """Computes the description_vector for the product."""
        if not self._is_product_description_vectorization_enabled():
            return
        url = self.embed_service_url
        if not url:
            raise ValueError(
                _(
                    "The embed service URL is not set. Please configure it in the system parameters by setting the key 'alc_product_similarity_settings.embed_service_url'."
                )
            )
        rqst = {
            "texts": [p._get_description_vector_input_text() for p in self],
        }

        response = requests.post(
            url=f"{url}/embed/products",
            json=rqst,
            headers={"Content-Type": "application/json"},
            timeout=60,
        )
        response.raise_for_status()
        embeddings = response.json().get("embeddings")
        for product, vector in zip(self, embeddings, strict=True):
            product.description_vector = vector

    def _get_characteristics_infos(self):
        """
        Extracts the characteristics infos that will be used for similarity search.

        Note that the extracted characteristics are not the same depending on the type if the item.

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

    def get_similar_products(self, limit):
        """
        Retrieves similar products based on vector distances.

        (Do not return this product in the list)

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

        query = self._search([("id", "!=", self.id)])
        from_clause, where_clause, where_clause_params = query.get_sql()

        sql = f"""
        SELECT
            product_product.id,
            product_product.characteristics_vector <=> %s,
            product_product.description_vector <=> %s
        FROM
            {from_clause}
        WHERE
            {where_clause}
        ORDER BY
            product_product.characteristics_vector <=> %s,
            product_product.description_vector <=> %s
        LIMIT
            {limit}
        """
        params = (
            self.characteristics_vector,
            self.description_vector,
            *where_clause_params,
            self.characteristics_vector,
            self.description_vector,
        )
        self.env.cr.execute(sql, params)

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
