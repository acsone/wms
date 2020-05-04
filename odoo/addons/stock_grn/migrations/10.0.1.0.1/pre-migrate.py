# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Create and initialize the grn_date field on stock.picking")

    cr.execute(
        """
        SELECT
            1
        FROM
            information_schema.columns
        WHERE
            table_name='stock_picking'
            AND column_name='grn_date';
    """
    )
    if cr.fetchall():
        _logger.into("Column already exists; Skip!")
        return

    cr.execute(
        """
        ALTER  TABLE
            stock_picking
        ADD COLUMN
            grn_date TIMESTAMP WITHOUT TIME ZONE;
        """
    )
    cr.execute(
        """
        UPDATE
            stock_picking
        SET
            grn_date = stock_grn.date
        FROM
            stock_grn
        WHERE stock_picking.grn_id = stock_grn.id
    """
    )
