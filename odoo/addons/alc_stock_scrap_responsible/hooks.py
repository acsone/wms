# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo.tools import sql

_logger = logging.getLogger(__name__)


def pre_init_hook(cr) -> None:
    _logger.info("alc_stock_scrap_responsible: copy operator_id into user_id")
    if not sql.column_exists(cr, "stock_scrap", "user_id"):
        cr.execute(
            """
            ALTER TABLE stock_scrap
            ADD COLUMN user_id INTEGER
            """
        )
    if sql.column_exists(cr, "stock_scrap", "operator_id"):
        cr.execute(
            """
            UPDATE stock_scrap
            SET user_id = operator_id
            WHERE operator_id IS NOT NULL
            """
        )
        _logger.info("alc_stock_scrap_responsible: drop operator_id")
        cr.execute("ALTER TABLE stock_scrap DROP COLUMN operator_id")
