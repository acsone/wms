# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

_logger = logging.getLogger(__name__)


def _fill_partner_lat_long(cr, registry):
    _logger.info(
        "Move partner lat/long info from custom fields to specific fields"
    )
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
            SET partner_latitude = longitude,
                partner_longitude = latitude
        FROM
            x_partner_geolocalize
        WHERE ref=code;
        """
    )


def _geo_localize_main_company(cr, registry):
    _logger.info("Geo localize Alcyon Belux")
    cr.execute(
        """
        UPDATE
            res_partner
            SET partner_latitude = %s,
                partner_longitude = %s
        WHERE
            id = 1
        """,
        (50.5825464, 5.2758074),
    )


def post_init_hook(cr, registry):
    _fill_partner_lat_long(cr, registry)
    _geo_localize_main_company(cr, registry)
