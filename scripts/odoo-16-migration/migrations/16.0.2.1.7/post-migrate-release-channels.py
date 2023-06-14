# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def _create_geoengine_resources_from_delivery_resources(env):
    """Create geoengine resources from delivery resources."""
    # add column on release channel to keep reference of the corresponding delivery template
    cr = env.cr
    cr.execute(
        """
        ALTER TABLE toursolver_resource
        ADD COLUMN alc_delivery_resource_id INTEGER
        """
    )
    cr = env.cr
    _logger.info("Creating toursolver resources from delivery resources")
    cr.execute(
        """
        INSERT INTO toursolver_resource (
            alc_delivery_resource_id,
            toursolver_backend_id,
            partner_id,
            name,
            resource_id,
            use_delivery_person_coordinates_as_end,
            active
            )
        SELECT
            id,
            %s,
            delivery_person_id,
            name,
            geo_optimization_resource_id,
            use_delivery_person_coordinates_as_end,
            True
        FROM alc_delivery_resource
        """,
        (env.ref("shipment_advice_planner_toursolver.toursolver_backend_default").id,),
    )
    _logger.info("Created %s toursolver resources from delivery resources", cr.rowcount)


def _link_resources_to_release_channels(env):
    """Link toursolver resources to release channels."""
    cr = env.cr
    _logger.info("Linking toursolver resources to release channels")
    cr.execute(
        """
            INSERT into stock_release_channel_toursolver_resource_rel (
                stock_release_channel_id,
                toursolver_resource_id
            )
            SELECT
                stock_release_channel.id,
                toursolver_resource.id
            FROM stock_release_channel
            JOIN alc_delivery_resource_round_template_rel ON
                alc_delivery_resource_round_template_rel.round_template_id = stock_release_channel.round_template_id
            JOIN toursolver_resource ON
                toursolver_resource.alc_delivery_resource_id = alc_delivery_resource_round_template_rel.alc_delivery_resource_id
        """,
    )
    _logger.info("Linked %s toursolver resources to release channels", cr.rowcount)


@openupgrade.migrate()
def migrate(env, version):
    _create_geoengine_resources_from_delivery_resources(env)
    _link_resources_to_release_channels(env)
