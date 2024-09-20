# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def _update_existing_package_types(env):
    # Setting existing Boites to category 'Médicaments'
    _logger.info("Updating Médicaments boxes")
    category = env.ref(
        "alc_stock_package_type_category_data.alc_package_type_category_medicament"
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
    ali = env.ref(
        "alc_stock_package_type_category_data.alc_package_type_category_aliment"
    )
    frigo = env.ref(
        "alc_stock_package_type_category_data.alc_package_type_category_frigo"
    )
    materiel = env.ref(
        "alc_stock_package_type_category_data.alc_package_type_category_materiel"
    )
    categories = ali | frigo | materiel
    for category in categories:
        for i in range(1, 11):
            str_i = str(i)
            package_type_obj.create(
                {
                    "name": f"Boîte {str_i}",
                    "category_id": category.id,
                    "package_carrier_type": "none",
                    "number_of_parcels": i,
                    "barcode": f"T#BOITE{str_i}{category.code}",
                }
            )


def _update_existing_package_types_other(env):
    # Setting existing package types (PAL, etc...)
    _logger.info("Updating Médicaments package types")
    category = env.ref(
        "alc_stock_package_type_category_data.alc_package_type_category_medicament"
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
    for package_type in package_types:
        nbr = str(package_type.number_of_parcels)
        package_type.write({"category_id": category.id})

    category = env.ref(
        "alc_stock_package_type_category_data.alc_package_type_category_aliment"
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
    for package_type in package_types:
        nbr = str(package_type.number_of_parcels)
        package_type.write({"barcode": f"T#BOITE{nbr}ALI", "category_id": category.id})

    category = env.ref(
        "alc_stock_package_type_category_data.alc_package_type_category_frigo"
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
    for package_type in package_types:
        nbr = str(package_type.number_of_parcels)
        package_type.write({"category_id": category.id})

    category = env.ref(
        "alc_stock_package_type_category_data.alc_package_type_category_materiel"
    )
    _logger.info("Updating Materiel package types")
    package_types = env["stock.package.type"].search(
        [
            ("name", "like", "E %"),
            ("package_carrier_type", "=", False),
            ("category_id", "=", False),
        ]
    )
    for package_type in package_types:
        nbr = str(package_type.number_of_parcels)
        package_type.write({"category_id": category.id})


def _create_and_update_package_types_for_internal_packages(env):
    # Create package types for TA / TM / PA packages
    # and affect it to them
    package_type_obj = env["stock.package.type"]

    # Aliments
    category = env.ref(
        "alc_stock_package_type_category_data.alc_package_type_category_aliment"
    )

    # PA
    pa = package_type_obj.create(
        {
            "name": "PA1 Interne",
            "package_carrier_type": False,
            "category_id": category.id,
        }
    )
    packages = env["stock.quant.package"].search(
        [
            ("is_internal", "=", True),
            ("name", "like", "PA1-%"),
            ("package_type_id", "=", False),
        ]
    )
    packages.write(
        {
            "package_type_id": pa.id,
        }
    )

    # TA09
    ta09 = package_type_obj.create(
        {
            "name": "TA09 Interne",
            "package_carrier_type": False,
            "category_id": category.id,
        }
    )
    packages = env["stock.quant.package"].search(
        [
            ("is_internal", "=", True),
            ("name", "like", "TA09-%"),
            ("package_type_id", "=", False),
        ]
    )
    packages.write(
        {
            "package_type_id": ta09.id,
        }
    )

    # TA1
    ta1 = package_type_obj.create(
        {
            "name": "TA1 Interne",
            "package_carrier_type": False,
            "category_id": category.id,
        }
    )
    packages = env["stock.quant.package"].search(
        [
            ("is_internal", "=", True),
            ("name", "like", "TA1-%"),
            ("package_type_id", "=", False),
        ]
    )
    packages.write(
        {
            "package_type_id": ta1.id,
        }
    )

    # TA12
    ta12 = package_type_obj.create(
        {
            "name": "TA12 Interne",
            "package_carrier_type": False,
            "category_id": category.id,
        }
    )
    packages = env["stock.quant.package"].search(
        [
            ("is_internal", "=", True),
            ("name", "like", "TA12-%"),
            ("package_type_id", "=", False),
        ]
    )
    packages.write(
        {
            "package_type_id": ta12.id,
        }
    )

    # Médicaments
    category = env.ref(
        "alc_stock_package_type_category_data.alc_package_type_category_medicament"
    )

    # TM1
    tm1 = package_type_obj.create(
        {
            "name": "TM1 Interne",
            "package_carrier_type": False,
            "category_id": category.id,
        }
    )
    packages = env["stock.quant.package"].search(
        [
            ("is_internal", "=", True),
            ("name", "like", "TM1-%"),
            ("package_type_id", "=", False),
        ]
    )
    packages.write(
        {
            "package_type_id": tm1.id,
        }
    )
    # TM6
    tm6 = package_type_obj.create(
        {
            "name": "TM6 Interne",
            "package_carrier_type": False,
            "category_id": category.id,
        }
    )
    packages = env["stock.quant.package"].search(
        [
            ("is_internal", "=", True),
            ("name", "like", "TM6-%"),
            ("package_type_id", "=", False),
        ]
    )
    packages.write(
        {
            "package_type_id": tm6.id,
        }
    )


@openupgrade.migrate()
def migrate(env, version):
    _update_existing_package_types(env)
    _create_new_package_types(env)
    _update_existing_package_types_other(env)
    _create_and_update_package_types_for_internal_packages(env)
