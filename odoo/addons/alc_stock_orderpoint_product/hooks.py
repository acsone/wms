# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from openupgradelib import openupgrade


def pre_init_hook(cr):
    openupgrade.update_module_names(
        cr,
        [("stock_orderpoint_product", "alc_stock_orderpoint_product")],
        merge_modules=True,
    )
