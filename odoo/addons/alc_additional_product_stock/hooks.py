# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from openupgradelib import openupgrade


def pre_init_hook(cr):

    # Moved fields from alc_b2c_connector
    openupgrade.update_module_moved_fields(
        cr,
        "stock.move",
        [
            "is_additional_move",
            "main_move_id",
            "additional_move_ids",
        ],
        "product_additional",
        "alc_additional_product_stock",
    )
