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

    _logger.info("Fill picking_type_subcode on stock_picking")

    if not column_exists(cr, "stock_picking", "picking_type_subcode"):
        cr.execute(
            """
            ALTER TABLE stock_picking
            ADD COLUMN picking_type_subcode varchar;
        """
        )
        cr.execute(
            """
            UPDATE stock_picking
            SET picking_type_subcode = t.subcode
            FROM stock_picking_type t
            WHERE t.id = stock_picking.picking_type_id
        """
        )
