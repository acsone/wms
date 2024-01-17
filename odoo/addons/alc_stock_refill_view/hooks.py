# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo.tools import sql

_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    """This function will be executed before installing the module."""
    # We create the field picking_type_id in column in the stock_move_line table
    # if it does not exist yet and we fill the value for all the rows in
    # state not done nor cancel
    if not sql.column_exists(cr, "stock_move_line", "picking_type_id"):
        _logger.info("Add column picking_type_id in stock_move_line table")
        cr.execute(
            """
            ALTER TABLE stock_move_line
            ADD COLUMN picking_type_id INTEGER
        """
        )
        cr.execute(
            """
            UPDATE stock_move_line
            SET picking_type_id = (
                SELECT picking_type_id
                FROM stock_picking
                WHERE stock_picking.id = stock_move_line.picking_id
            )
            WHERE state NOT IN ('done', 'cancel')
        """
        )
        _logger.info("%s rows updated in stock_move_line table", cr.rowcount)
