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

    _logger.info("Fill location_kind on stock_quant")

    if not column_exists(cr, "stock_quant", "location_kind"):
        cr.execute(
            """
            ALTER TABLE stock_quant
            ADD COLUMN location_kind varchar;
        """
        )
        cr.execute(
            """
            UPDATE stock_quant
            SET location_kind = l.kind
            FROM stock_location l
            WHERE l.id = stock_quant.location_id
        """
        )
