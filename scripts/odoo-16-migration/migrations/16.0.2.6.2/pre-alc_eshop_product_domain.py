# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def migrate(cr, version):
    data = [
        (
            "alc_eshop.shopinvader_assortment_store",
            "alc_eshop_product_domain.shopinvader_assortment_store",
        )
    ]
    openupgrade.rename_xmlids(cr, data, allow_merge=True)
