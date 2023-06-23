# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def _create_release_channels_from_delivery_rounds(env):
    """Create release channels from delivery rounds."""
    cr = env.cr
    # add column on release channel to keep reference of the corresponding delivery template
    cr.execute(
        """
        ALTER TABLE stock_release_channel
        ADD COLUMN round_template_id INTEGER
        """
    )

    _logger.info("Creating release channels from delivery template for toursolver")
    cr.execute(
        """
        INSERT INTO stock_release_channel (
            name,
            channel_code,
            shape_name,
            release_mode,
            batch_mode,
            restrict_to_delivery_zone,
            delivery_zone,
            shipment_planning_method,
            sequence,
            shipment_advice_arrival_delay,
            round_template_id,
            active,
            state,
            rule_domain
        )
        SELECT
            name,
            code,
            shape_name,
            'auto',
            'max',
            True,
            geo_polygon_shape,
            'toursolver',
            time_picking_planned,
            time_leave_planned,
            id,
            active,
            'asleep',
            '[]'
        FROM
            round_template
        WHERE
            geo_polygon_shape IS NOT NULL
        """,
    )
    _logger.info(
        "Created %s release channels from delivery template for toursolver", cr.rowcount
    )

    _logger.info("Creating release channels from delivery template for simple")
    cr.execute(
        """
        INSERT INTO stock_release_channel (
            name,
            channel_code,
            shape_name,
            release_mode,
            batch_mode,
            shipment_planning_method,
            sequence,
            shipment_advice_arrival_delay,
            round_template_id,
            active,
            state,
            rule_domain
        )
        SELECT
            name,
            code,
            shape_name,
            'auto',
            'max',
            'simple',
            time_picking_planned,
            time_leave_planned,
            id,
            active,
            'asleep',
            '[]'
        FROM
            round_template
        WHERE
            geo_polygon_shape IS NULL
            """,
    )
    _logger.info(
        "Created %s release channels from delivery template for simple", cr.rowcount
    )

    # Open release channels if delivery round is not closed
    _logger.info("Opening release channels")
    cr.execute(
        """
        UPDATE
            stock_release_channel
        SET
            state = 'open'
        FROM
            round_instance ri
        WHERE
            ri.state != 'done'
            AND ri.template_id = stock_release_channel.round_template_id;
        """
    )
    _logger.info("Opened %s release channels", cr.rowcount)

    # fill release channel tags relation table
    # round_tag table has been renamed to alc_stock_release_channel_tag into a
    # pre-migrate script
    _logger.info("Creating release channel tags relations")
    cr.execute(
        """
        INSERT INTO alc_stock_release_channel_tag_stock_release_channel_rel (
            stock_release_channel_id,
            alc_stock_release_channel_tag_id
        )
        SELECT
            stock_release_channel.id,
            round_tag_id
        FROM
            round_tag_round_template_rel
            JOIN stock_release_channel
                ON round_tag_round_template_rel.round_template_id = stock_release_channel.round_template_id
            """,
    )
    _logger.info("Created %s release channel tags relations", cr.rowcount)

    # declare picking types to be managed by release channels
    _logger.info("Declaring picking types to be managed by release channels")
    cr.execute(
        """
        UPDATE
            stock_picking_type
        SET
            release_channel_can_allow_pick = True
        WHERE
            name->>'fr_BE' like 'Pick%';
        """
    )
    _logger.info(
        "Declared %s picking types to be managed by release channels", cr.rowcount
    )


def _create_shipment_advice_from_round_instances(env):
    """Create shipment advices from round instances."""
    cr = env.cr
    # add column on shipment advice to keep reference of the corresponding delivery instance
    # and its index
    cr.execute(
        """
        ALTER TABLE shipment_advice
        ADD COLUMN round_instance_id INTEGER
        """
    )
    cr.execute(
        """
        CREATE INDEX ON shipment_advice (round_instance_id)
        """
    )
    # create one shipment advice per round instance
    _logger.info("Creating shipment advices from round instances")
    cr.execute(
        """
        INSERT INTO shipment_advice (
            name,
            state,
            release_channel_id,
            round_instance_id,
            shipment_type,
            departure_date,
            arrival_date,
            warehouse_id
        )
        SELECT
            round_instance.complete_name,
            'done',
            stock_release_channel.id,
            round_instance.id,
            'outgoing',
            round_instance.write_date,
            round_instance.write_date,
            1
        FROM
            round_instance
            JOIN stock_release_channel
                ON round_instance.template_id = stock_release_channel.round_template_id
        WHERE
            round_instance.state = 'done'
    """
    )
    _logger.info("Created %s shipment advices from delivery instances", cr.rowcount)

    # reference the shipment advice on the stock.move
    _logger.info("Linking stock moves to shipment advices")
    cr.execute(
        """
        UPDATE stock_move
        SET shipment_advice_id = shipment_advice.id
        FROM shipment_advice
            JOIN stock_picking
                ON shipment_advice.round_instance_id = stock_picking.delivery_round_id
            JOIN stock_picking_type
                ON stock_picking.picking_type_id = stock_picking_type.id
        WHERE
            stock_move.picking_id = stock_picking.id
            AND stock_picking.delivery_round_id IS NOT NULL
            AND stock_move.state = 'done'
            AND stock_picking_type.code IN ('outgoing', 'internal')
        """
    )
    _logger.info("Updated %s stock move with shipment advice", cr.rowcount)

    # reference the shipment advice on the stock.picking
    # As planned_shipment_advice_id is a related on first stock move
    # shipment_advice_id field, we limit the select to 1
    _logger.info("Linking stock picking to shipment advices")
    cr.execute(
        """
        UPDATE stock_picking
            SET planned_shipment_advice_id =
                (SELECT shipment_advice_id
                    FROM stock_move
                        WHERE picking_id = stock_picking.id
                        AND shipment_advice_id IS NOT NULL LIMIT 1)
            WHERE EXISTS (
                SELECT 1 FROM stock_move
                WHERE picking_id = stock_picking.id
                AND shipment_advice_id IS NOT NULL);
        """
    )
    _logger.info("Updated %s stock picking with shipment advice", cr.rowcount)

    # set shipment advice on stock.move.line
    _logger.info("Linking stock move lines to shipment advices")
    cr.execute(
        """
        UPDATE
            stock_move_line
        SET
            shipment_advice_id = stock_move.shipment_advice_id
        FROM
            stock_move
        WHERE
            stock_move_line.move_id = stock_move.id
            AND stock_move.shipment_advice_id IS NOT NULL
        """
    )
    _logger.info("Updated %s stock move lines with shipment advice", cr.rowcount)


def _link_pickings_to_release_channels(env):
    """Link pickings to release channels."""
    cr = env.cr
    # link pickings to delivery instances
    _logger.info("Linking pickings to delivery instances")
    cr.execute(
        """
        UPDATE
            stock_picking
        SET
            release_channel_id = stock_release_channel.id
        FROM
            stock_release_channel,
            round_instance
        WHERE
            stock_picking.delivery_round_id IS NOT NULL
            AND stock_picking.release_channel_id IS NULL
            AND stock_release_channel.round_template_id = round_instance.template_id
            AND round_instance.id = stock_picking.delivery_round_id
        """
    )
    _logger.info("Updated %s stock pickings with delivery instances", cr.rowcount)


@openupgrade.migrate()
def migrate(env, version):
    _create_release_channels_from_delivery_rounds(env)
    _create_shipment_advice_from_round_instances(env)
    _link_pickings_to_release_channels(env)
