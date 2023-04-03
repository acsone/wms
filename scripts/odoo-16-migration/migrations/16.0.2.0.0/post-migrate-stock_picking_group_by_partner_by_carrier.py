# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Create relation between SO and picking by filling the.

    sale_order_stock_picking_rel table
    """
    _logger.info("Create relation between SO and picking")
    cr.execute(
        """
        INSERT INTO sale_order_stock_picking_rel (order_id, picking_id)
        SELECT
            so.id,
            sm.picking_id
        FROM
            stock_move as sm
            JOIN sale_order so
            ON so.procurement_group_id = sm.group_id
        WHERE sm.picking_id IS NOT NULL AND so.id IS NOT NULL
        GROUP BY so.id, sm.picking_id;
    """
    )
    _logger.info(f"{cr.rowcount} rows inserted in sale_order_stock_picking_rel")
