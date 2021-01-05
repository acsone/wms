# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from openupgradelib import openupgrade


def pre_init_hook(cr):
    """Loaded before installing the module.
    :param odoo.sql_db.Cursor cr:
        Database cursor.

    """
    # Moved fields from alc_b2c_connector
    openupgrade.update_module_moved_fields(
        cr,
        "res.partner",
        ["purchase_manager_id", "substitute_purchase_manager_id"],
        "specific_purchase",
        "alc_supplier_purchase_manager",
    )
