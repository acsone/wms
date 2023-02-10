# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

XML_IDS = [
    "not_specified",
    "all",
    "other",
    "cattle",
    "bird",
    "bee",
    "mouse",
    "cat",
    "chinchilla",
    "dog",
    "ferret",
    "goat",
    "guinea_pig",
    "horse",
    "pig",
    "pigeon",
    "poultry",
    "rabbit",
    "rat",
    "reptile",
    "sheep",
]


def pre_init_hook(cr):
    openupgrade.update_module_moved_fields(
        cr,
        "animal.species",
        ["name"],
        "product_animal_species",
        "alc_product_animal_species",
    )
    openupgrade.update_module_moved_fields(
        cr,
        "product.template",
        ["species_id", "species_ids"],
        "product_animal_species",
        "alc_product_animal_species",
    )
    openupgrade.rename_xmlids(
        cr,
        [
            (f"product_animal_species.{xml_id}", f"alc_product_animal_species.{xml_id}")
            for xml_id in XML_IDS
        ],
    )
