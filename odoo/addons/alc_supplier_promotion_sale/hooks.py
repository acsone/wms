# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from openupgradelib import openupgrade


def pre_init_hook(cr):

    # Moved fields from alc_b2c_connector
    openupgrade.update_module_moved_fields(
        cr,
        "sale.order.line",
        ["is_promotional_product"],
        "product_additional",
        "alc_supplier_promotion_sale",
    )
