# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from openupgradelib import openupgrade


def pre_init_hook(cr):
    # Move field from purchase_prepaid
    openupgrade.update_module_moved_fields(
        cr,
        "purchase.order",
        ["prepayment"],
        "purchase_prepaid",
        "alc_purchase_prepaid",
    )
