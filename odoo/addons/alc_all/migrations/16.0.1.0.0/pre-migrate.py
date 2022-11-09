# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.tools import sql

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    addons_to_uninstall = [
        "alc_stock_picking_policy_block",
        "stock_reassign_auto",
        "stock_picking_assignment",
    ]
    for addon in addons_to_uninstall:
        _logger.info("uninstall %s", ",".join(addon))
        cr.execute(
            "update ir_module_module set state = 'to remove' where name = %s",
            (addon,),
        )
    _migrate_stock_picking_assignment(cr)


def _migrate_stock_picking_assignment(cr):
    _logger.info("picking_assignment: copy operator_id into user_id")
    if sql.column_exists(cr, "stock_picking", "operator_id"):
        cr.execute(
            """
            UPDATE stock_picking
            SET user_id = operator_id
            WHERE operator_id IS NOT NULL
            """
        )
        _logger.info("picking_assignment: drop operator_id")
        cr.execute("ALTER TABLE stock_picking DROP COLUMN operator_id")
