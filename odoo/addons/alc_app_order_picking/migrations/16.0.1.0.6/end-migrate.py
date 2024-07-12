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


@openupgrade.migrate()
def migrate(env, version):
    _update_existing_package_types(env)
    _create_new_package_types(env)
