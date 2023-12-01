# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Odoo has put restrict_lot_id field in x_restrict_lot_id
    # (Migration scripts not frozen ...)
    if openupgrade.column_exists(env.cr, "stock_move", "x_restrict_lot_id"):
        query = """
            UPDATE stock_move SET restrict_lot_id = x_restrict_lot_id WHERE restrict_lot_id IS NULL AND x_restrict_lot_id IS NOT NULL;
        """
        openupgrade.logged_query(env.cr, query)
