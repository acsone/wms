# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Initialize newpharma ref")

    cr.execute(
        """
    UPDATE
        sale_order
    SET
        newpharma_ref = esb_ref
    WHERE
        partner_id in (select id from res_partner where  ref in ('8114', '8264'))
    """
    )

    cr.execute(
        """
    UPDATE
        sale_order_line
    SET
        newpharma_ref = esb_ref
    WHERE
        order_partner_id in (select id from res_partner where  ref in ('8114', '8264'))
    """
    )
    if not version:
        return
    return
