# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Uninstall alc_rma_sale_operation_required")
    cr.execute(
        """
      UPDATE ir_module_module
      SET state='to remove'
      WHERE name = 'alc_rma_sale_operation_required'
      """
    )
