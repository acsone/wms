# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from openupgradelib import openupgrade


def pre_init_hook(cr):

    # Moved fields from alc_b2c_connector
    openupgrade.update_module_moved_fields(
        cr,
        "product.supplierinfo",
        [
            "is_null_date_start",
            "discount_purchase",
            "discount_sale",
            "min_qty_sale",
            "min_qty",
        ],
        "pricelist_discount",
        "alc_product_supplierinfo_check",
    )
