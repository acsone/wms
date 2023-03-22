# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def pre_init_hook(cr):
    openupgrade.rename_xmlids(
        cr,
        [("specific_data.product_categ_ali", "alc_product_food.product_categ_ali")],
    )
    # If the module alc_product_category_data is installed, we need to rename
    # the xmlid of the product category
    openupgrade.rename_xmlids(
        cr,
        [
            (
                "alc_product_category_data.product_categ_ali",
                "alc_product_food.product_categ_ali",
            )
        ],
    )
