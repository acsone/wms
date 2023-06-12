# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.update_module_moved_fields(
        env.cr,
        "product.template",
        [
            "number_labels_to_print",
        ],
        "specific_print",
        "alc_product_label_printing",
    )

    openupgrade.update_module_moved_fields(
        env.cr,
        "res.partner",
        [
            "no_labels_products",
            "no_labels_food_products",
        ],
        "alc_label_printing_base",
        "alc_product_label_printing",
    )
