#!/usr/bin/env python

import xml.etree.ElementTree as ET

import click
import click_odoo
import numpy as np
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

from odoo import api
from odoo.tools import sql

text_embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

WORDS_EMBEDDING_DIM = 384

SPECIES_VECTOR_DIMENSION = 30
ANIMAL_SIZE_DIMENSION = 3
CATEG_AGE_DIMENSION = 3
FOOD_RANGE_DIMENSION = 40
INDICATION_DIMENSION = 20
PRESENTATION_DIMENSION = 10
ACTIVE_PRINCIPLE_DIMENSION = 400
ADMINISTRATION_ROUTE_DIMENSION = 30
CATEG_MEDICAL_DIMENSION = 150
TOTAL_CARACTERISTICS_DIM = (
    SPECIES_VECTOR_DIMENSION
    + ANIMAL_SIZE_DIMENSION
    + CATEG_AGE_DIMENSION
    + FOOD_RANGE_DIMENSION
    + INDICATION_DIMENSION
    + PRESENTATION_DIMENSION
    + ACTIVE_PRINCIPLE_DIMENSION
    + ADMINISTRATION_ROUTE_DIMENSION
    + CATEG_MEDICAL_DIMENSION
)


def normalize_vector(vector):
    """Normalizes a vector to have unit norm."""
    norm = np.linalg.norm(vector)
    if norm == 0:
        return vector  # Evite la division par 0
    return vector / norm


def one_hot_encode(value, options, dimension):
    """Encodes a single value as one-hot."""
    vector = np.zeros(dimension)
    if value in options:
        vector[options.index(value)] = 1
    return normalize_vector(vector)


def multi_hot_encode(values, options, dimension):
    """Encodes multiple values as multi-hot."""
    vector = np.zeros(dimension)
    for value in values:
        if value in options:
            vector[options.index(value)] = 1
    return normalize_vector(vector)


# def distance(v1, v2):
#     assert len(v1) == len(v2), "The vectors should have the same length"
#     return sum([abs(x-y) for x, y in zip(v1, v2)])/len(v1)


class VectorGenerator:
    def __init__(self, env):
        # set the lang to french into an environment
        self.env = api.Environment(env.cr, env.uid, dict(env.context, lang="fr_BE"))
        self.species = list(env["animal.species"].search([], order="id"))
        self.attribute_values = env["attribute.option"].search([], order="id")
        self.animal_sizes = list(
            self.attribute_values.filtered(
                lambda x: x.attribute_id.name == "animal_size_option_ids"
            )
        )
        self.categ_ages = list(
            self.attribute_values.filtered(
                lambda x: x.attribute_id.name == "categ_age_option_ids"
            )
        )
        self.food_ranges = list(
            self.attribute_values.filtered(
                lambda x: x.attribute_id.name == "food_range_option_id"
            )
        )
        self.indications = list(
            self.attribute_values.filtered(
                lambda x: x.attribute_id.name == "indication_option_ids"
            )
        )
        self.presentations = list(
            self.attribute_values.filtered(
                lambda x: x.attribute_id.name == "presentation_option_id"
            )
        )
        self.active_principles = list(
            self.attribute_values.filtered(
                lambda x: x.attribute_id.name == "active_principle_option_ids"
            )
        )
        self.administration_routes = list(
            self.attribute_values.filtered(
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
        env.cr.execute(SQL)
        ids = [x[0] for x in env.cr.fetchall()]
        self.medical_categories = list(env["product.category"].browse(ids))

    def _get_species_vector(self, species):
        return multi_hot_encode(species, self.species, SPECIES_VECTOR_DIMENSION)

    def _get_animal_size_vector(self, sizes):
        return multi_hot_encode(sizes, self.animal_sizes, ANIMAL_SIZE_DIMENSION)

    def _get_categ_age_vector(self, ages):
        return multi_hot_encode(ages, self.categ_ages, CATEG_AGE_DIMENSION)

    def _get_food_range_vector(self, range):
        return one_hot_encode(range, self.food_ranges, FOOD_RANGE_DIMENSION)

    def _get_indication_vector(self, indications):
        return multi_hot_encode(indications, self.indications, INDICATION_DIMENSION)

    def _get_presentation_vector(self, presentation):
        return one_hot_encode(presentation, self.presentations, PRESENTATION_DIMENSION)

    def _get_active_principle_vector(self, active_principles):
        return multi_hot_encode(
            active_principles, self.active_principles, ACTIVE_PRINCIPLE_DIMENSION
        )

    def _get_administration_route_vector(self, administration_routes):
        return multi_hot_encode(
            administration_routes,
            self.administration_routes,
            ADMINISTRATION_ROUTE_DIMENSION,
        )

    def _get_medical_category_vector(self, categories):
        return multi_hot_encode(
            categories, self.medical_categories, CATEG_MEDICAL_DIMENSION
        )

    def _ensure_vector_colum_exists(self):
        if not sql.column_exists(
            self.env.cr, "product_product", "caracteristics_vector"
        ):
            sql.create_column(
                self.env.cr,
                "product_product",
                "caracteristics_vector",
                f"vector({TOTAL_CARACTERISTICS_DIM})",
            )
        if not sql.column_exists(self.env.cr, "product_product", "description_vector"):
            sql.create_column(
                self.env.cr,
                "product_product",
                "description_vector",
                f"vector({WORDS_EMBEDDING_DIM})",
            )

    def get_caracteristics_vector(self, product):
        species = product.species_ids
        sizes = product.animal_size_option_ids
        ages = product.categ_age_option_ids
        food_range = product.food_range_option_id
        indications = product.indication_option_ids
        presentation = product.presentation_option_id
        active_principles = product.active_principle_option_ids
        administration_route = product.administration_route_option_ids
        medical_categories = product.categ_ids.filtered(
            lambda x: x in self.medical_categories
        )
        vectors = []
        if product.is_meds:
            vectors.extend(
                [
                    self._get_medical_category_vector(medical_categories),
                    2
                    * self._get_active_principle_vector(
                        active_principles
                    ),  # -> *2 to give more weight to active principles
                    self._get_administration_route_vector(administration_route),
                ]
            )
        else:
            vectors.extend(
                [
                    self._get_medical_category_vector(medical_categories.browse()),
                    self._get_active_principle_vector(active_principles.browse()),
                    self._get_administration_route_vector(
                        administration_route.browse()
                    ),
                ]
            )

        if product.is_meds or product.is_food:
            vectors.append(self._get_species_vector(species))
        else:
            vectors.append(self._get_species_vector(species.browse()))

        if product.is_food:
            vectors.extend(
                [
                    self._get_food_range_vector(food_range),
                    self._get_animal_size_vector(sizes),
                    self._get_categ_age_vector(ages),
                    self._get_indication_vector(indications),
                    self._get_presentation_vector(presentation),
                ]
            )
        else:
            vectors.extend(
                [
                    self._get_food_range_vector(food_range.browse()),
                    self._get_animal_size_vector(sizes.browse()),
                    self._get_categ_age_vector(ages.browse()),
                    self._get_indication_vector(indications.browse()),
                    self._get_presentation_vector(presentation.browse()),
                ]
            )
        return np.concatenate(vectors)

    def create_xml_representation(self, product, save_folder: str | None = None) -> str:
        species = product.species_ids
        sizes = product.animal_size_option_ids
        ages = product.categ_age_option_ids
        food_range = product.food_range_option_id
        indications = product.indication_option_ids
        presentation = product.presentation_option_id
        active_principles = product.active_principle_option_ids
        administration_route = product.administration_route_option_ids
        medical_categories = product.categ_ids.filtered(
            lambda x: x in self.medical_categories
        )
        description = product.description_shop_long

        root = ET.Element("product")
        ET.SubElement(root, "title").text = product.name
        for attribute, attribute_name in [
            (species, "species"),
            (sizes, "sizes"),
            (ages, "ages"),
            (food_range, "food_range"),
            (indications, "indications"),
            (presentation, "presentation"),
            (active_principles, "active_principles"),
            (administration_route, "administration_route"),
            (medical_categories, "medical_categories"),
        ]:
            if attribute:
                ET.SubElement(root, attribute_name).text = ",".join(
                    [value.name for value in attribute]
                )
        if description:
            ET.SubElement(root, "description").text = description

        # Create the ElementTree object
        tree = ET.ElementTree(root)

        # Write the XML to a file
        if save_folder:
            tree.write(
                f"{save_folder}/{product.default_code}.xml",
                encoding="unicode",
                xml_declaration=False,
            )
        return ET.tostring(root, encoding="unicode")

    def get_description_vector(self, product):
        description = product.name + (
            ("\n" + str(product.description_shop_long))
            if product.description_shop_long
            else ""
        )

        return text_embedding_model.encode(description, show_progress_bar=False)

    def index_product(self, product):
        caracteristics_vector = self.get_caracteristics_vector(product)
        description_vector = self.get_description_vector(product)
        self.env.cr.execute(
            """
            UPDATE
                product_product
            SET
                caracteristics_vector = %s,
                description_vector = %s
            WHERE
                id = %s""",
            (
                caracteristics_vector.tolist(),
                description_vector.tolist(),
                product.id,
            ),
        )

    def index_product_xml(self, product, vector):
        self.env.cr.execute(
            """
            UPDATE
                product_product
            SET
                xml_embedding = %s
            WHERE
                id = %s""",
            (
                vector.tolist(),
                product.id,
            ),
        )

    def index_products(self, products_domain: list[tuple]):
        self._ensure_vector_colum_exists()
        products = self.env["product.product"].search(products_domain)
        for product in tqdm(products, desc="Indexing products", total=len(products)):
            self.index_product(product)
        self.env.cr.commit()


@click.command()
@click_odoo.env_options()
def main(env):
    generator = VectorGenerator(env)
    generator.index_products([])
    # generator.index_products([("product_brand_id", "=", 15)])


if __name__ == "__main__":
    main()
