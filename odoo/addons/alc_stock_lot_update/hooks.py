# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from openupgradelib import openupgrade


def pre_init_hook(cr):
    """Loaded before installing the module.

    :param odoo.sql_db.Cursor cr:
        Database cursor.
    """
    openupgrade.update_module_names(
        cr, [("stock_lot_update", "alc_stock_lot_update")], merge_modules=True
    )
