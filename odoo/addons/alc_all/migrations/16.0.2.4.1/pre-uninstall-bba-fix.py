# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Uninstall l10n_be_bba_fix ")
    cr.execute(
        """
      UPDATE ir_module_module
      SET state='to remove'
      WHERE name = 'l10n_be_bba_fix'
      """
    )
