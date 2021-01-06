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
    openupgrade.update_module_names(
        cr,
        [("specific_purchase_report", "alc_oeel_purchase_report")],
        merge_modules=True,
    )

    # Moved fields from specific_purchase
    openupgrade.update_module_moved_fields(
        cr,
        "purchase.order",
        ["last_date_done"],
        "specific_purchase",
        "alc_oeel_purchase_report",
    )
