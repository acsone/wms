# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def pre_init_hook(cr):
    """Loaded before installing the module.
    :param odoo.sql_db.Cursor cr:
        Database cursor.

    """
    # Moved fields from stock_barcode_fix
    openupgrade.update_module_moved_fields(
        cr,
        "stock.location",
        ["barcode_picking_type_id"],
        "stock_barcode_fix",
        "alc_stock_barcode_picking_type",
    )
