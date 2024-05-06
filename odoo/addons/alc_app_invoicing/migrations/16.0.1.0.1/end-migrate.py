# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    """Set up purchase journal."""
    _logger.info("Set 'Avoid Zero Lines' on Purchase Journal")
    journal = env.ref(
        "__setup__.account_journal_vendor_bills", raise_if_not_found=False
    )
    if journal:
        journal.write(
            {
                "avoid_zero_lines": True,
            }
        )
