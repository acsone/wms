# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _remove_product_bin(cr):
    """Remove the module stock_product_bin."""
    query = """
        UPDATE ir_module_module
            SET state = 'to remove'
            WHERE name = 'stock_product_bin'
    """
    openupgrade.logged_query(cr, query)


def migrate(cr, version):
    _remove_product_bin(cr)
