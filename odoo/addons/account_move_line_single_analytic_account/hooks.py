# Copyright (C) 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    """Quick populate new analytic_account_id field to avoid.

    slowness if this is done by the ORM, in the case of
    installation of this module on a large database.
    """
    if openupgrade.table_exists(cr, "account_invoice_line"):
        _logger.info("Initialize 'analytic_account_id' field")
        cr.execute(
            """
            ALTER TABLE account_move_line
            ADD COLUMN analytic_account_id INTEGER
            """
        )

        cr.execute(
            """
            UPDATE account_move_line
            SET analytic_account_id = map.account_analytic_id
            FROM (SELECT ivl.account_analytic_id, iam.aml_id
              FROM account_invoice_line ivl JOIN invl_aml_mapping iam
              ON ivl.id = iam.invl_id) as map
            WHERE id = map.aml_id
            """
        )
