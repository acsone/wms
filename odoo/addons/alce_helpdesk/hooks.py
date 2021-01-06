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
        cr, [("specific_helpdesk", "alce_helpdesk")], merge_modules=True
    )
