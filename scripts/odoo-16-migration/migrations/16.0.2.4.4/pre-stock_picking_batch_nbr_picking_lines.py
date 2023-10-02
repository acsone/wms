# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def _create_and_init_nbr_picking_lines_column(cr):
    _logger.info("Create and initialize the column nbr_picking_lines")
    cr.execute(
        """
        ALTER TABLE stock_picking ADD COLUMN IF NOT EXISTS nbr_picking_lines integer;
        UPDATE stock_picking
        SET nbr_picking_lines = (
            SELECT count(1)
            FROM stock_move_line
            WHERE picking_id = stock_picking.id
        ) WHERE state='assigned' and nbr_picking_lines is null;
        """
    )


@openupgrade.migrate()
def migrate(env, version):
    _create_and_init_nbr_picking_lines_column(env.cr)
