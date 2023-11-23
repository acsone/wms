# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def migrate(cr, version):
    data = [
        (
            "specific_security.group_product_assortment_manager",
            "alc_product_assortment.group_product_assortment_manager",
        )
    ]
    openupgrade.rename_xmlids(cr, data, allow_merge=True)
