# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from sentence_transformers import SentenceTransformer

from odoo import api, fields, models, tools

from .alc_product_characteristic import AlcProductCharacteristic


class ProductProduct(models.Model):
    _name = "product.product"
    _inherit = "product.product"

    _text_embedding_model = None  # lazy loading of the text embedding model
    TEXT_EMBEDDING_DIM = None  # 384 (lazy loading)

    characteristics_vector = fields.Text(
        string="Characteristics vector",
        readonly=True,
        compute="_compute_characteristics_vector",
        store=True,
    )
    description_vector = fields.Text(
        string="Description vector",
        readonly=True,
        compute="_compute_description_vector",
        store=True,
    )

    @api.depends("name", "description_shop_long")
    def _compute_description_vector(self):
        """Computes the description_vector for the product."""
        for product in self:
            product.description_vector = product._get_description_vector()

    @api.model
    @tools.ormcache()
    def _get_total_number_characteristics(self):
        species = list(self.env["animal.species"].search([], order="id"))
        attribute_values = self.env["attribute.option"].search([], order="id")
        animal_sizes = list(
            attribute_values.filtered(
                lambda x: x.attribute_id.name == "animal_size_option_ids"
            )
        )
        categ_ages = list(
            attribute_values.filtered(
                lambda x: x.attribute_id.name == "categ_age_option_ids"
            )
        )
        food_ranges = list(
            attribute_values.filtered(
                lambda x: x.attribute_id.name == "food_range_option_id"
            )
        )
        indications = list(
            attribute_values.filtered(
                lambda x: x.attribute_id.name == "indication_option_ids"
            )
        )
        presentations = list(
            attribute_values.filtered(
                lambda x: x.attribute_id.name == "presentation_option_id"
            )
        )
        active_principles = list(
            attribute_values.filtered(
                lambda x: x.attribute_id.name == "active_principle_option_ids"
            )
        )
        administration_routes = list(
            attribute_values.filtered(
                lambda x: x.attribute_id.name == "administration_route_option_ids"
            )
        )
        # SELECT name from leaf categories into medical
        SQL = """
            select
                id
            from
                product_category
            where
                id not in (
                    select
                        distinct pc.parent_id
                    from
                        product_category pc
                    where
                        parent_id is not null
                )
                and complete_name like 'Catalogue Alcyon / Drugs /%'
            order by id;
        """
        self.env.cr.execute(SQL)
        ids = [x[0] for x in self.env.cr.fetchall()]
        medical_categories = list(self.env["product.category"].browse(ids))

        return len(
            [
                *species,
                *animal_sizes,
                *categ_ages,
                *food_ranges,
                *indications,
                *presentations,
                *active_principles,
                *administration_routes,
                *medical_categories,
            ]
        )

    def _get_characteristics_infos(self):
        """
        Extracts the characteristics infos that will be used for similarity search (the extarcted characteristics are not the same depending on the type if the item).

        Returns:
            list[tuple]: a list of tuples of the form (<characteristic_record>, <characteristic_name>, <characteristic_weight>)
        """
        self.ensure_one()

        main_species = self.species_id
        species = self.species_ids
        sizes = self.animal_size_option_ids
        ages = self.categ_age_option_ids
        food_range = self.food_range_option_id
        indications = self.indication_option_ids
        presentation = self.presentation_option_id
        active_principles = self.active_principle_option_ids
        administration_route = self.administration_route_option_ids
        medical_categories = self.categ_ids.filtered(
            lambda x: x in self.medical_categories
        )

        infos = []
        if self.is_meds:
            infos.extend([(x, "categ_ids", 1) for x in medical_categories])
            infos.extend(
                [(x, "active_principle_option_ids", 2) for x in active_principles]
            )
            infos.extend(
                [
                    (x, "administration_route_option_ids", 1)
                    for x in administration_route
                ]
            )

        if self.is_meds or self.is_food:
            infos.extend([(x, "species_ids", 1) for x in species])
            infos.extend([(x, "species_id", 1) for x in main_species])

        if self.is_food:
            infos.extend([(x, "food_range_option_id", 1) for x in food_range])
            infos.extend([(x, "animal_size_option_ids", 1) for x in sizes])
            infos.extend([(x, "categ_age_option_ids", 1) for x in ages])
            infos.extend([(x, "indication_option_ids", 1) for x in indications])
            infos.extend([(x, "presentation_option_id", 1) for x in presentation])

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
        total_number_characteristics = self._get_total_number_characteristics()
        vector_dim = self._get_characteristics_vector_dim()

        # if the size of the vector is too small to fit all characteristics, double the size and re-index all records
        if total_number_characteristics > vector_dim:
            new_vector_dim = 2 * vector_dim
            self._set_characteristics_vector_dim(new_vector_dim)
            for record in self.search([]):
                record._compute_characteristics_vector()
            return

        for record in self:
            characteristics_infos = record._get_characteristics_infos()
            vector_indices_and_weights = AlcProductCharacteristic(
                self.env
            ).get_vector_indices_and_weights(
                [infos[0] for infos in characteristics_infos],
                [infos[1] for infos in characteristics_infos],
                [infos[2] for infos in characteristics_infos],
            )
            vector = [0 for _ in range(vector_dim)]
            for index, weight in vector_indices_and_weights.values():
                vector[index] = weight
            record.characteristics_vector = str(vector)

    @api.model
    def _get_text_embedding_model(self):
        if not ProductProduct._text_embedding_model:
            ProductProduct._text_embedding_model = SentenceTransformer(
                "paraphrase-multilingual-MiniLM-L12-v2",
            )
        return ProductProduct._text_embedding_model

    @api.model
    def _get_text_embedding_dim(self):
        if not ProductProduct.TEXT_EMBEDDING_DIM:
            ProductProduct.TEXT_EMBEDDING_DIM = (
                self._get_text_embedding_model().encode("dummy input").shape[0]
            )
        return ProductProduct.TEXT_EMBEDDING_DIM

    def _get_characteristics_vector_data(self):
        return [float(x) for x in self.characteristics_vector.strip("[]").split(",")]

    def _get_description_vector_data(self):
        return [float(x) for x in self.description_vector.strip("[]").split(",")]

    def _get_description_vector(self):
        description = self.name + (
            ("\n" + str(self.description_shop_long))
            if self.description_shop_long
            else ""
        )

        return str(
            self._get_text_embedding_model()
            .encode(description, show_progress_bar=False)
            .tolist()
        )

    def get_similar_products(self, limit):
        """
        Retrieves similar products based on vector distances.

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

        # 3. Perform the query using raw SQL (for vector operations)
        query = f"""
            SELECT
                id,
                pp.characteristics_vector::vector <=> %s::vector,
                pp.description_vector::vector <=> %s::vector
            FROM
                product_product AS pp
            WHERE
                pp.id != %s
            ORDER BY
                pp.characteristics_vector::vector <=> %s::vector,
                pp.description_vector::vector <=> %s::vector
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
