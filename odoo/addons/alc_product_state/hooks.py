# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from openupgradelib import openupgrade


def pre_init_hook(cr):
    """Loaded before installing the module.²
    :param odoo.sql_db.Cursor cr:
        Database cursor.

    """
    openupgrade.update_module_moved_fields(
        cr,
        "product.state",
        ["name", "sequence", "code"],
        "specific_purchase",
        "alc_product_state",
    )
    to_rename = [
        "product_state_a",
        "product_state_d",
        "product_state_h",
        "product_state_i",
        "product_state_l",
        "product_state_m",
        "product_state_n",
    ]
    openupgrade.rename_xmlids(
        cr,
        [
            ("specific_purchase.%s" % xml_id, "alc_product_state.%s" % xml_id)
            for xml_id in to_rename
        ],
    )
