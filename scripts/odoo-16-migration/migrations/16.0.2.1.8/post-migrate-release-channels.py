# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def _fix_partners_in_geo_release_channels(env):
    """Fix partners in release channels linked to geo optimization templates."""
    cr = env.cr
    _logger.info("Fixing partners in geo release channels")
    cr.execute(
        """
    UPDATE
        res_partner
    SET
        in_geo_release_channel = False
    WHERE
        not_in_dynamic_delivery_round is not True
        """
    )


def _link_partners_to_release_channels(env):
    """Link partners to release channels if they where linked to a delivery template through.

    an delivery itinerary.
    """
    cr = env.cr
    _logger.info("Linking partners to release channels")
    cr.execute(
        """
    INSERT INTO res_partner_stock_release_channel_rel
    (
        partner_id,
        channel_id
    )
    SELECT
        distinct(position.partner_id),
        channel.id
    FROM
        round_itinerary_position position
        JOIN round_itinerary itinerary ON position.itinerary_id = itinerary.id
        JOIN round_itinerary_round_template_rel irt ON irt.round_itinerary_id = itinerary.id
        JOIN round_template ON irt.round_template_id = round_template.id
        JOIN stock_release_channel channel ON channel.round_template_id = round_template.id
        JOIN res_partner rp on rp.id = position.partner_id
    WHERE
        rp.in_geo_release_channel is False
    group by position.partner_id, channel.id
        """,
    )
    _logger.info("Linked %s toursolver resources to release channels", cr.rowcount)


@openupgrade.migrate()
def migrate(env, version):
    _fix_partners_in_geo_release_channels(env)
    _link_partners_to_release_channels(env)
