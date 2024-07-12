# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def _update_channels_auto_process(env):
    """Default channels should be set as auto deliver (except Comptoir, etc.)."""

    # Not Comptoir, SAV, Long Terme
    channels = env["stock.release.channel"].search([("id", "not in", (170, 182, 239))])

    channels.write(
        {
            "auto_deliver": True,
        }
    )


def _uninstall_alc_module(env):
    query = """
        UPDATE ir_module_module
            SET state = 'to remove'
            WHERE name = 'alc_stock_release_channel_deliver'
    """
    openupgrade.logged_query(env.cr, query)


@openupgrade.migrate()
def migrate(env, version):
    _update_channels_auto_process(env)
    _uninstall_alc_module(env)
