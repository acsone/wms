# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def pre_init_hook(cr):
    """Loaded before installing the module.
    :param odoo.sql_db.Cursor cr:
        Database cursor.

    """
    # Moved fields from alc_b2c_connector
    openupgrade.update_module_moved_fields(
        cr, "product.template", ["is_mto_product"], "specific_stock", "alc_product_mto"
    )
