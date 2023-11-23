# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    openupgrade.rename_xmlids(
        cr[
            (
                "specific_cutoff.ir_cron_cutoff_expense",
                "alc_account_invoice_accrual.ir_cron_cutoff_expense",
            ),
            (
                "specific_cutoff.ir_cron_cutoff_revenue",
                "alc_account_invoice_accrual.ir_cron_cutoff_revenue",
            ),
        ],
    )
