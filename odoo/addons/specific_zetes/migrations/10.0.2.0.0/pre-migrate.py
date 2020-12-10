# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def column_exists(cr, tablename, columnname):
    """ Return whether the given column exists. """
    query = """ SELECT 1 FROM information_schema.columns
                WHERE table_name=%s AND column_name=%s """
    cr.execute(query, (tablename, columnname))
    return cr.rowcount


def migrate(cr, version):
    if not version:
        return

    _logger.info("Fill zetes_logger_requires_check on stock_picking")

    if not column_exists(cr, "stock_picking", "zetes_logger_requires_check"):
        cr.execute(
            """
            ALTER TABLE stock_picking
            ADD COLUMN zetes_logger_requires_check boolean;
        """
        )
        cr.execute(
            """
            UPDATE stock_picking
            SET zetes_logger_requires_check = false;
        """
        )

    _logger.info("Fill requires_check on zetes_logger")

    if not column_exists(cr, "zetes_logger", "requires_check"):
        cr.execute(
            """
            ALTER TABLE zetes_logger
            ADD COLUMN requires_check boolean;
        """
        )
        cr.execute(
            """
            UPDATE zetes_logger
            SET requires_check = false;
        """
        )
    if not column_exists(cr, "zetes_logger", "to_check"):
        cr.execute(
            """
            ALTER TABLE zetes_logger
            ADD COLUMN to_check boolean;
        """
        )
        cr.execute(
            """
            UPDATE zetes_logger
            SET to_check = false;
        """
        )
