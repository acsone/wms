# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.update_module_moved_fields(
        env.cr,
        "product.pricelist",
        ("role_name", "discount_role_name"),
        "pricelist_role_name",
        "alc_pricelist_role_name",
    )
