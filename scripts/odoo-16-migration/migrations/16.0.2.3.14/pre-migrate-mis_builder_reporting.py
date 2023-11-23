# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def _migrate_data(cr):
    # Remove l10n_be_mis_reports xmlids to avoid name changing in migrated data
    # and keep noupdate=False reports unchanged
    _logger.info("Remove l10n_be_mis_reports xmlids")
    openupgrade.logged_query(
        cr,
        """
        DELETE FROM ir_model_data
        WHERE module = 'l10n_be_mis_reports'
        """,
    )

    # some report instances are not used so remove them
    # VAT 2019 - 02 Control / 27
    # PP / 4
    # Bilan / 3
    # Belgium Value Added Tax Report Sheet / 7
    # Marge avec comparatif mensuel(J - E) / 22
    _logger.info("Removing 5 Mis report instances with ids: 3, 4, 7, 22, 27")
    cr["mis.report.instance"].browse([3, 4, 7, 22, 27]).unlink()


def migrate(cr, version):
    _migrate_data(cr)
