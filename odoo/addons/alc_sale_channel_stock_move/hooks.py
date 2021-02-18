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


def _update_sale_order_line(cr):
    _logger.info("Update sale channel on sale order line")
    if not column_exists(cr, "sale_order_line", "sale_channel"):
        cr.execute(
            """
        ALTER TABLE sale_order_line
         ADD sale_channel VARCHAR
        """
        )

    cr.execute(
        """
        UPDATE sale_order_line sol
            SET
                sale_channel = so.sale_channel
            FROM sale_order so
            WHERE so.id = sol.order_id
    """
    )


def pre_init_hook(cr):
    _update_sale_order_line(cr)
