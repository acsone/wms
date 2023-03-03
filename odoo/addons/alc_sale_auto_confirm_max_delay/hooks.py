# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from openupgradelib import openupgrade


def pre_init_hook(cr):
    openupgrade.update_module_names(
        cr, [("sale_delay", "alc_sale_auto_confirm_max_delay")], merge_modules=True
    )
