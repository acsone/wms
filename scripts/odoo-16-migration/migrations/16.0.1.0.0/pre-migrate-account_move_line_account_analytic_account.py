# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# TODO should be executed right after the Odoo migration

import logging

from odoo.tools import sql

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("account_move_line: restore analytic_account_id")
    if sql.column_exists(cr, "account_move_line", "x_analytic_account_id"):
        _logger.info("account_move_line: add field analytic_account_id")
        cr.execute(
            "ALTER TABLE account_move_line " "ADD COLUMN analytic_account_id INTEGER"
        )
        _logger.info(
            "account_move_line: copy x_analytic_account_id to " "analytic_account_id"
        )
        cr.execute(
            """
            UPDATE account_move_line
            SET analytic_account_id = x_analytic_account_id
            WHERE x_analytic_account_id IS NOT NULL
            """
        )
    else:
        _logger.info(
            "account_move_line: retrieve analytic_account_id from invoice lines"
        )
        cr.execute(
            """
            UPDATE account_move_line aml
            SET analytic_account_id = ivl.account_analytic_id
            FROM invl_aml_mapping iam, account_invoice_line ivl
            WHERE aml.id=iam.aml_id and ivl.id = iam.invl_id
            """
        )
