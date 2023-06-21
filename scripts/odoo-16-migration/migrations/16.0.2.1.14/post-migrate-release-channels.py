# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def _migrate_delivery_plan(env):
    """Migrate delivery plan."""
    cr = env.cr
    _logger.info("Creating delivery plan")
    cr.execute(
        """
        DELETE FROM alc_delivery_plan;
        INSERT INTO alc_delivery_plan (
            id,
            name,
            active
        )
        SELECT
            id,
            name,
            active
        FROM delivery_plan;
        """,
    )
    _logger.info("Created %s delivery plan", cr.rowcount)

    _logger.info("Link release channels to delivery plan")
    cr.execute(
        """
            UPDATE
                stock_release_channel
            SET
                delivery_plan_id = (
                    SELECT
                        delivery_plan_id
                    FROM
                        round_template rt
                    WHERE
                        rt.id = stock_release_channel.round_template_id
                );

        """
    )
    _logger.info("Linked %s release channels to delivery plan", cr.rowcount)


def _migrate_round_template_version(env):
    _logger.info("Creating ock Release Channel Preparation Plan")
    cr = env.cr
    cr.execute(
        """
            INSERT INTO stock_release_channel_preparation_plan (
                id,
                name,
                active
            )
            SELECT
                id,
                name,
                active
            FROM
                round_template_version;
        """
    )
    _logger.info("Created %s stock Release Channel Preparation Plan", cr.rowcount)

    _logger.info("Link stock Release Channel Preparation Plan to stock Release Channel")
    cr.execute(
        """
        INSERT INTO stock_release_channel_preparation_plan_rel (
            plan_id,
            channel_id
        )
        SELECT
            round_template_version_id,
            stock_release_channel.id
        FROM
            round_template_round_template_version_rel rel
            JOIN stock_release_channel
                ON rel.round_template_id = stock_release_channel.round_template_id;
    """
    )
    _logger.info(
        "Linked %s stock Release Channel Preparation Plan to stock Release Channel",
        cr.rowcount,
    )


@openupgrade.migrate()
def migrate(env, version):
    _migrate_delivery_plan(env)
    _migrate_round_template_version(env)
