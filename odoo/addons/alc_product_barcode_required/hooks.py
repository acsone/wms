# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def pre_init_hook(cr):
    """Loaded before installing the module.
    :param odoo.sql_db.Cursor cr:
        Database cursor.

    """
    # Moved field from alc_product_audit
    openupgrade.update_module_moved_fields(
        cr,
        "product.template",
        ["no_barcode_authorized"],
        "alc_product_audit",
        "alc_product_barcode_required",
    )
