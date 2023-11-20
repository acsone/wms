# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def _migrate_sale_orders(env):
    """
    Move all sale orders state from sale to done.

    The reason is that the sale_order_line_cancel wizard needs a locked SO to operates.
    One example in cancel BO older than 3 months
    """
    query = """
        UPDATE sale_order
            SET state = 'done'
            WHERE state = 'sale'
    """
    openupgrade.logged_query(env.cr, query)


@openupgrade.migrate()
def migrate(env, version):
    _migrate_sale_orders(env)
