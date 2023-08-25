# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

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
