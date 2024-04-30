# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

from odoo.tools import sql


def migrate(cr, version):
    """Remove obsolete FK."""

    if sql.column_exists(cr, "stock_move_line", "additional_move_id"):
        query = """
          alter table stock_move_line drop column additional_move_id ;
        """
        openupgrade.logged_query(cr, query)
