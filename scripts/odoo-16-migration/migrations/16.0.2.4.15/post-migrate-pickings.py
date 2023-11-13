# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def _migrate_pickings(env):
    """
    Unrelease all OUT pickings related to internal ones that are in 'confirmed' state and:

    - have a void release channel
    - a picking type in : Pick M, Pick aliments, Pick matériel, Pick frigo, Pick inconnu
    """
    picking_type_ids = [16, 15, 18, 24, 3]

    pickings = env["stock.picking"].search(
        [
            ("state", "in", ["confirmed", "assigned"]),
            ("printed", "=", False),
            ("release_channel_id", "=", False),
            ("picking_type_id", "in", picking_type_ids),
        ]
    )
    _logger.info(
        "Following pickings will be unreleased: %(picking_names)s",
        {"picking_names": ",".join(pickings.mapped("name"))},
    )
    pickings.mapped("move_ids.move_dest_ids.picking_id").unrelease(True)


@openupgrade.migrate()
def migrate(env, version):
    _migrate_pickings(env)
