# Copyright 2023 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def _migrate_cutoff(env):
    _logger.info("Migrate existing cutoffs")
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE account_cutoff
            SET cutoff_type = type, order_line_model = 'purchase.order.line'
            WHERE type = 'accrued_expense'
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE account_cutoff
            SET cutoff_type = type, order_line_model = 'sale.order.line'
            WHERE type = 'accrued_revenue'
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE account_cutoff
            SET cutoff_type = type
            WHERE cutoff_type IS NULL
        """,
    )
    openupgrade.logged_query(env.cr, "ALTER TABLE account_cutoff DROP COLUMN type")


@openupgrade.migrate()
def migrate(env, version):
    _migrate_cutoff(env)
