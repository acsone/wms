# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

_logger = logging.getLogger(__name__)


def _migrate_order_line_to_sale_line(cr):
    """Put info of order_line_id to sale_line_id on the stock move."""
    _logger.info("Updating sale_line_id with order_line_id")
    cr.execute(
        """
        UPDATE
            stock_move
        SET
            sale_line_id = order_line_id
        WHERE
            order_line_id IS NOT NULL;
        """
    )


def migrate(cr, version):
    _migrate_order_line_to_sale_line(cr)
