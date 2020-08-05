# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Fix qty_delivered for order move done after 2020-08-04 10:00:00")
    if not version:
        return
    sql = """
    SELECT
        distinct(po.sale_line_id)
    FROM
        procurement_order po
        JOIN stock_move sm on sm.procurement_id=po.id
        JOIN product_product pp on pp.id = sm.product_id
        JOIN product_template pt on pt.id = pp.product_tmpl_id
            and pt.additional_product_id is not null
    WHERE
        sm.state='done'
        AND sm.write_date > '2020-08-04 10:00:00'
        AND po.sale_line_id is not null
    """
    cr.execute(sql)
    ids = [r[0] for r in cr.fetchall()]
    env = api.Environment(cr, SUPERUSER_ID, {})
    for line in env["sale.order.line"].browse(ids):
        line.qty_delivered = line._get_delivered_qty()
    return
