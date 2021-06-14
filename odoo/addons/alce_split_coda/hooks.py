# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
from openupgradelib import openupgrade


def pre_init_hook(cr):
    """Loaded before installing the module.
    :param odoo.sql_db.Cursor cr:
        Database cursor.

    """
    openupgrade.update_module_names(
        cr, [("split_coda", "alce_split_coda")], merge_modules=True
    )
