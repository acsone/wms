# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo.tools import sql

_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    """This function will be executed before installing the module."""
    # We create the field priority in column in the stock_move_line table
    # if it does not exist yet and we fill the value for all the rows in
    # state not done nor cancel
    if not sql.column_exists(cr, "stock_move_line", "priority"):
        _logger.info("Add column priority in stock_move_line table")
        cr.execute(
            """
            ALTER TABLE stock_move_line
            ADD COLUMN priority VARCHAR DEFAULT '0'
        """
        )
        cr.execute(
            """
            UPDATE stock_move_line
            SET priority = stock_move.priority
            FROM stock_move
            WHERE stock_move_line.move_id = stock_move.id
            AND stock_move.state NOT IN ('done', 'cancel')
            AND stock_move.priority IS NOT NULL AND stock_move.priority != '0'
        """
        )
        _logger.info("%s rows updated in stock_move_line table", cr.rowcount)
