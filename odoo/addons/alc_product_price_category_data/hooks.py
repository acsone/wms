# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

IDS = {
    "product_price_category_ali",
    "product_price_category_alg",
    "product_price_category_alh",
    "product_price_category_gma",
    "product_price_category_imp",
}


def pre_init_hook(cr):

    # Moved xml_id from specific_data
    openupgrade.rename_xmlids(
        cr,
        [
            (f"specific_product.{xml_id}", f"alc_product_price_category_data.{xml_id}")
            for xml_id in IDS
        ],
    )
