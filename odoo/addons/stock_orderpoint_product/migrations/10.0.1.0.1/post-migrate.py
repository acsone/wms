# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Update orderpoints min/max on products")
    if not version:
        return

    cr.execute(
        """
            UPDATE product_product pp
            SET orderpoint_min = swo.product_min_qty,
                orderpoint_max = swo.product_max_qty,
                orderpoint_qty_multiple = swo.qty_multiple
            FROM stock_warehouse_orderpoint swo WHERE swo.product_id = pp.id;
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
