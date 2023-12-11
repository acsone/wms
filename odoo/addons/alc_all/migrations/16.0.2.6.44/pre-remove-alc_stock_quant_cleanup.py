# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """
    Remove alc_stock_quant_cleanup.

    after !2215, the queue job now effectively manages concurrency issues between
    shipment a advice auto_process jobs. In the event of a failure, it's promptly retried.
    The alc_stock_quant_cleanup function is no longer necessary, and we can revert to
    the standard where cleaning quants is done after picking validation.
    """
    _logger.info("Uninstall alc_stock_quant_cleanup")
    cr.execute(
        """
      UPDATE ir_module_module
      SET state='to remove'
      WHERE name = 'alc_stock_quant_cleanup'
      """
    )
