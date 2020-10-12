# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def pre_init_hook(cr):
    openupgrade.update_module_names(
        cr, [("stock_unit", "alc_product_packaging_stock_reserve")], merge_modules=True
    )
