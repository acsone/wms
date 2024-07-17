# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def _update_existing_package_types(env):
    # Setting existing Boites to category 'Médicaments'
    _logger.info("Updating Médicaments boxes")
    category = env.ref(
        "alc_stock_package_type_category.alc_package_type_category_medicament"
    )
    package_types = env["stock.package.type"].search(
        [
            ("package_carrier_type", "=", "none"),
            ("name", "like", "Boîte%"),
            ("category_id", "=", False),
        ]
    )
    package_types.write({"category_id": category.id})


def _create_new_package_types(env):
    # Create missing boxes types
    _logger.info("Creating missing boxes")
    package_type_obj = env["stock.package.type"]
    ali = env.ref("alc_stock_package_type_category.alc_package_type_category_aliment")
    frigo = env.ref("alc_stock_package_type_category.alc_package_type_category_frigo")
    materiel = env.ref(
        "alc_stock_package_type_category.alc_package_type_category_materiel"
    )
    categories = ali | frigo | materiel
    for category in categories:
        for i in range(10):
            str_i = str(i)
            package_type_obj.create(
                {
                    "name": f"Boîte {str_i}",
                    "category_id": category.id,
                    "package_carrier_type": "none",
                    "number_of_parcels": i,
                }
            )


def _update_existing_package_types_other(env):
    # Setting existing package types (PAL, etc...)
    _logger.info("Updating Médicaments package types")
    category = env.ref(
        "alc_stock_package_type_category.alc_package_type_category_medicament"
    )
    package_types = env["stock.package.type"].search(
        [
            "|",
            ("name", "like", "M %"),
            ("name", "like", "Inflammable %"),
            ("package_carrier_type", "=", False),
            ("category_id", "=", False),
        ]
    )
    package_types.write({"category_id": category.id})

    category = env.ref(
        "alc_stock_package_type_category.alc_package_type_category_aliment"
    )
    _logger.info("Updating Aliments package types")
    package_types = env["stock.package.type"].search(
        [
            "|",
            ("name", "like", "A %"),
            ("name", "like", "AG %"),
            ("package_carrier_type", "=", False),
            ("category_id", "=", False),
        ]
    )
    package_types.write({"category_id": category.id})

    category = env.ref(
        "alc_stock_package_type_category.alc_package_type_category_frigo"
    )
    _logger.info("Updating Frigo package types")
    package_types = env["stock.package.type"].search(
        [
            "|",
            ("name", "like", "Frigo %"),
            ("name", "like", "Q %"),
            ("package_carrier_type", "=", False),
            ("category_id", "=", False),
        ]
    )
    package_types.write({"category_id": category.id})

    category = env.ref(
        "alc_stock_package_type_category.alc_package_type_category_materiel"
    )
    _logger.info("Updating Materiel package types")
    package_types = env["stock.package.type"].search(
        [
            ("name", "like", "E %"),
            ("package_carrier_type", "=", False),
            ("category_id", "=", False),
        ]
    )
    package_types.write({"category_id": category.id})


@openupgrade.migrate()
def migrate(env, version):
    _update_existing_package_types(env)
    _create_new_package_types(env)
    _update_existing_package_types_other(env)
