# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Update variant id based on product template id")
    if not version:
        return

    cr.execute(
        """
        UPDATE
            product_stock_bin psb
            SET variant_id = pp.id
        FROM
            product_product pp
        WHERE pp.product_tmpl_id = psb.product_id;
        """
    )
