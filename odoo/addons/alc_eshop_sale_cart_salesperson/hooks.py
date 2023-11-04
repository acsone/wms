# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def pre_init_hook(cr):
    openupgrade.rename_xmlids(
        cr,
        [
            (
                "alc_eshop_salesperson.eshop_salesperson",
                "alc_eshop_sale_cart_salesperson.eshop_salesperson",
            )
        ],
    )
