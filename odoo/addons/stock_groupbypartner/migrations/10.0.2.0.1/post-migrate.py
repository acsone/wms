# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return

    _logger.info("Set customer on procurement group for procurement linked to SO")

    cr.execute(
        """
            UPDATE
                procurement_group
            SET
                customer_id = so.partner_id
            FROM sale_order so
            WHERE
                procurement_group.name like 'SO%'
                AND so.name = procurement_group.name
        """
    )
