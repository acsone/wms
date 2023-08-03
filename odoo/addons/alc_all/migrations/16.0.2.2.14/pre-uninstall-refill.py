# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Uninstall stock_refill ")
    cr.execute(
        """
      UPDATE ir_module_module
      SET state='to remove'
      WHERE name = 'stock_refill'
      """
    )

    # rename column reserve_location_id to x_reserve_location_id on stock_location required for migration script
    cr.execute(
        """
        ALTER TABLE stock_location RENAME COLUMN reserve_location_id TO x_reserve_location_id
    """
    )

    _logger.info("Uninstall delivery_rounds_refill ")
    cr.execute(
        """
      UPDATE ir_module_module
      SET state='to remove'
      WHERE name = 'delivery_rounds_refill'
      """
    )
