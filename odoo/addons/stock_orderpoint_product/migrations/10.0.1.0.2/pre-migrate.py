# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def column_exists(cr, tablename, columnname):
    """ Return whether the given column exists. """
    query = """ SELECT 1 FROM information_schema.columns
                WHERE table_name=%s AND column_name =%s """
    cr.execute(query, (tablename, columnname))
    return cr.rowcount


def migrate(cr, version):
    _logger.info("Update orderpoints min/max on products")
    if not version:
        return

    if not column_exists(cr, "product_product", "orderpoint_min"):
        cr.execute(
            """
        ALTER TABLE product_product
         ADD orderpoint_min DOUBLE PRECISION
        """
        )
    if not column_exists(cr, "product_product", "orderpoint_max"):
        cr.execute(
            """
        ALTER TABLE product_product
         ADD orderpoint_max DOUBLE PRECISION
        """
        )
    if not column_exists(cr, "product_product", "orderpoint_qty_multiple"):
        cr.execute(
            """
        ALTER TABLE product_product
         ADD orderpoint_qty_multiple DOUBLE PRECISION
        """
        )
    cr.execute(
        """
            UPDATE product_product pp
            SET orderpoint_min = swo.product_min_qty,
                orderpoint_max = swo.product_max_qty,
                orderpoint_qty_multiple = swo.qty_multiple
            FROM stock_warehouse_orderpoint swo WHERE swo.product_id = pp.id;
        """
    )

    if not column_exists(cr, "product_template", "orderpoint_min"):
        cr.execute(
            """
        ALTER TABLE product_template
         ADD orderpoint_min DOUBLE PRECISION
        """
        )
    if not column_exists(cr, "product_template", "orderpoint_max"):
        cr.execute(
            """
        ALTER TABLE product_template
         ADD orderpoint_max DOUBLE PRECISION
        """
        )
    if not column_exists(cr, "product_template", "orderpoint_qty_multiple"):
        cr.execute(
            """
        ALTER TABLE product_template
         ADD orderpoint_qty_multiple DOUBLE PRECISION
        """
        )
    cr.execute(
        """
            UPDATE product_template pt
            SET orderpoint_min = pp.orderpoint_min,
                orderpoint_max = pp.orderpoint_max,
                orderpoint_qty_multiple = pp.orderpoint_qty_multiple
            FROM product_product pp WHERE pp.product_tmpl_id = pt.id;
        """
    )
