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
    _logger.info(
        "By default, all customers should have the flag of csv deliveryship sending to true"
    )
    if not column_exists(cr, "stock_picking", "delivery_note_supplier_number"):
        cr.execute(
            """
            ALTER TABLE stock_picking
            ADD COLUMN delivery_note_supplier_number VARCHAR;
        """
        )
    cr.execute(
        """
        UPDATE
            stock_picking
            SET delivery_note_supplier_number = ' ';
        """
    )
