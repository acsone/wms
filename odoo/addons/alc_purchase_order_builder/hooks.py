# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def pre_init_hook(cr):
    modules = [
        (
            "website_purchase_review",
            "alc_purchase_order_builder",
        )
    ]
    openupgrade.update_module_names(cr, modules, merge_modules=True)
