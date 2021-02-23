# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def pre_init_hook(cr):
    """Loaded before installing the module.
    :param odoo.sql_db.Cursor cr:
        Database cursor.

    """
    # Moved fields from alc_b2c_connector
    openupgrade.update_module_moved_fields(
        cr,
        "product.category",
        ["is_business_unit"],
        "code_abc",
        "alc_product_category_business_unit",
    )

    openupgrade.update_module_moved_fields(
        cr,
        "product.product",
        ["business_unit_id"],
        "code_abc",
        "alc_product_category_business_unit",
    )

    openupgrade.update_module_moved_fields(
        cr,
        "product.template",
        ["business_unit_id"],
        "code_abc",
        "alc_product_category_business_unit",
    )
