# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _init_blocked_field(env):
    """Initialize blocked_for_channel_assignation field (last version missed this)."""
    query = """
        UPDATE stock_picking sp
            SET blocked_for_channel_assignation = True
            WHERE EXISTS (SELECT 1 FROM stock_move
                            WHERE picking_id = sp.id
                            GROUP BY picking_id
                            HAVING SUM(CASE WHEN (
                                stock_move.delivery_requires_other_lines
                                AND NOT sp.ignore_release_channel_block) THEN 1 ELSE 0 END) = COUNT(*))
            AND sp.state NOT IN ('done', 'cancel');

    """
    openupgrade.logged_query(env.cr, query)


@openupgrade.migrate()
def migrate(env, version):
    _init_blocked_field(env)
