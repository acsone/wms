# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def _remove_channel(env):
    _logger.info("Remove channels")
    comptoir = env["stock.release.channel"].search([("name", "=", "Comptoir (2021)")])
    comptoir.write({"active": False})

    default = env.ref(
        "stock_release_channel.stock_release_channel_default", raise_if_not_found=False
    )
    if default:
        default.unlink()


@openupgrade.migrate()
def migrate(env, version):
    _remove_channel(env)
