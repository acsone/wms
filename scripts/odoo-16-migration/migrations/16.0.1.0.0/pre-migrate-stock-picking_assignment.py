# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.tools import sql

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("picking_assignment: copy operator_id into user_id")
    if sql.column_exists(cr, "stock_picking", "operator_id"):
        cr.execute(
            """
            UPDATE stock_picking
            SET user_id = operator_id
            WHERE operator_id IS NOT NULL and user_id IS NULL
            """
        )
        _logger.info("picking_assignment: drop operator_id")
        cr.execute("ALTER TABLE stock_picking DROP COLUMN operator_id")
