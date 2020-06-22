# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def _fill_partner_lat_long_or_geo_point(cr, registry):
    cr.execute(
        """
        UPDATE res_partner
        SET geo_point = ST_Transform(
            ST_SetSRID(ST_Point(partner_longitude, partner_latitude) , 4326),
            3857)
        WHERE partner_longitude is not null and partner_latitude is not null
        and geo_point is null
    """
    )

    cr.execute(
        """
        UPDATE res_partner
        SET partner_latitude = ST_Y(g.geom),
            partner_longitude =  ST_X(g.geom)
        FROM (SELECT
            id,
            ST_TRANSFORM(ST_SetSRID(geo_point, 3857), 4326) as geom
            FROM res_partner
            WHERE geo_point is not null and
                    partner_longitude is null and partner_latitude is null
        ) g
        WHERE res_partner.id = g.id
    """
    )


def post_init_hook(cr, registry):
    _fill_partner_lat_long_or_geo_point(cr, registry)
