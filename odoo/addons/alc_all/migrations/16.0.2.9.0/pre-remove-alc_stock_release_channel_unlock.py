# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Remove alc_stock_release_channel_unlock."""
    _logger.info("Uninstall alc_stock_release_channel_unlock")
    cr.execute(
        """
      UPDATE ir_module_module
      SET state='to remove'
      WHERE name = 'alc_stock_release_channel_unlock'
      """
    )
