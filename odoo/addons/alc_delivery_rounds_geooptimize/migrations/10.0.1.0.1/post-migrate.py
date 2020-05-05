# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Fix lat long")
    if not version:
        return

    cr.execute(
        """
        SELECT 1
        FROM information_schema.tables
        WHERE table_name = 'x_partner_geolocalize'
    """
    )
    res = cr.fetchall()
    if not res:
        _logger.info("x_partner_geolocalize no found")
        return
    cr.execute(
        """
        UPDATE
            res_partner
            SET partner_latitude = latitude,
                partner_longitude = longitude
        FROM
            x_partner_geolocalize
        WHERE ref=code;
        """
    )
