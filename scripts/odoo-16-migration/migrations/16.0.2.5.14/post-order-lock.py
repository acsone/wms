# Copyright 2023 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def _migrate_orders_locked(env):
    _logger.info("Mark locked sales order to invoice as fully invoiced")
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE sale_order
            SET force_invoiced = 't'
            WHERE state = 'done' and invoice_status = 'to invoice'
        """,
    )
    _logger.info("Locked all confirmed sales order")
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE sale_order
            SET state = 'done'
            WHERE state = 'sale'
        """,
    )
    _logger.info("Mark locked purchase order to invoice as fully invoiced")
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE purchase_order
            SET force_invoiced = 't'
            WHERE state = 'done' and invoice_status = 'to invoice'
        """,
    )
    _logger.info("Locked all confirmed purchase order")
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE purchase_order
            SET state = 'done'
            WHERE state = 'purchase'
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _migrate_orders_locked(env)
