# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Assign the good package types to the good abc profile
    profile_obj = env["abc.classification.profile"]
    package_type_obj = env["stock.package.type"]
    warehouse = env.ref("stock.warehouse0")

    # M Profile
    profile = profile_obj.browse(1)
    package_types = package_type_obj.search(
        [
            ("name", "=like", "M %"),
            ("name", "not like", "M Achet%"),
            ("name", "not like", "M Coli%"),
        ]
    )

    profile.package_type_ids = package_types

    # A Profile
    profile = profile_obj.browse(4)
    package_types = package_type_obj.search(
        [
            ("name", "=like", "A%"),
            ("name", "not like", "A Achet%"),
        ]
    )

    profile.package_type_ids = package_types

    # Creation

    # DG
    dg = profile_obj.create(
        {
            "name": "Zone DG",
            "profile_type": "sale_stock",
            "warehouse_id": warehouse.id,
        }
    )

    package_types = package_type_obj.search(
        [
            ("name", "=like", "Infla%"),
        ]
    )

    dg.package_type_ids = package_types

    # Q
    q = profile_obj.create(
        {
            "name": "Zone Q",
            "profile_type": "sale_stock",
            "warehouse_id": warehouse.id,
        }
    )

    package_types = package_type_obj.search(
        [
            ("name", "=like", "Q%"),
            ("name", "not like", "Q Achet%"),
            ("name", "not like", "Q Coli%"),
        ]
    )

    q.package_type_ids = package_types
