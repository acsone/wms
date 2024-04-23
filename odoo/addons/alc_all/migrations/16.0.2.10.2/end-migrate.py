# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def migrate(cr, version):
    """Remove obsolete FK."""

    query = """
        alter table stock_move_line drop column additional_move_id ;
      """
    openupgrade.logged_query(cr, query)
