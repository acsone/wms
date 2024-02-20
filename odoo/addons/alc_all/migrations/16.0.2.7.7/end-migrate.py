# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def migrate(cr, version):
    query = """
    UPDATE stock_picking_type
        SET backorder_reason_transparent_cancel = True
        WHERE id = 4
      """
    openupgrade.logged_query(cr, query)
