# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from openupgradelib import openupgrade


def pre_init_hook(cr):

    # Move fields from product_last_transaction
    openupgrade.update_module_moved_fields(
        cr,
        "product.product",
        ["product_last_in_date", "product_last_out_date"],
        "product_last_transaction",
        "alc_product_last_transaction",
    )
