# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def pre_init_hook(cr):
    openupgrade.rename_xmlids(
        cr,
        [
            (
                "alc_stock_storage_type.package_st_M_M_Nouveaute",
                "alc_product_is_new.package_st_M_M_Nouveaute",
            )
        ],
    )
