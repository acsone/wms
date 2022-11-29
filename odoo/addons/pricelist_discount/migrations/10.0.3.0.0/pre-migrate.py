# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

_logger = logging.getLogger(__name__)


def column_exists(cr, tablename, columnname):
    """ Return whether the given column exists. """
    query = """ SELECT 1 FROM information_schema.columns
                WHERE table_name=%s AND column_name=%s """
    cr.execute(query, (tablename, columnname))
    return cr.rowcount


def migrate(cr, version):
    _logger.info("Add discount_item_id")
    if not column_exists(cr, "sale_order_line", "discount_item_id"):
        cr.execute(
            """
            ALTER TABLE sale_order_line
            ADD COLUMN discount_item_id INTEGER;
        """
        )
