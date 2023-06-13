# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def migrate(cr, version):
    modules = [
        (
            "sock_reception_priority",
            "alc_stock_reception_rank",
        )
    ]
    openupgrade.update_module_names(cr, modules, merge_modules=True)

    SQL = """
        ALTER TABLE stock_picking DROP COLUMN qty_outofstock;
    """
    openupgrade.logged_query(cr, SQL)

    SQL = """
        ALTER TABLE stock_picking DROP COLUMN qty_backorder;
    """
    openupgrade.logged_query(cr, SQL)
    SQL = """
        ALTER TABLE stock_move_line DROP COLUMN qty_backorder;
    """
    openupgrade.logged_query(cr, SQL)
