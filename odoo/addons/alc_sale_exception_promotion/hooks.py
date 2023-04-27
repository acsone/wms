# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from openupgradelib import openupgrade


def pre_init_hook(cr):
    openupgrade.rename_xmlids(
        cr,
        [
            (
                "specific_sale.warning_free_product",
                "alc_sale_exception.warning_free_product",
            )
        ],
    )
