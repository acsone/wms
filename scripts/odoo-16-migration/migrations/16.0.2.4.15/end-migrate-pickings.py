# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

from odoo.fields import Command

_logger = logging.getLogger(__name__)


def _migrate_pickings(env):
    """
    Delete all pickings that are in 'confirmed' state and:

    - have a void relese channel
    - a picking type in : Pick M, Pick aliments, Pick matériel, Pick frigo, Pick inconnu
    """
    picking_type_ids = [16, 15, 18, 24, 3]

    pickings = env["stock.picking"].search(
        [
            ("state", "=", "confirmed"),
            ("printed", "=", False),
            ("release_channel_id", "=", False),
            ("picking_type_id", "in", picking_type_ids),
        ]
    )
    pickings.mapped("move_ids").write({"move_dest_ids": [Command.clear()]})
    if openupgrade.table_exists(env.cr, "stock_pack_operation_deleted"):
        query = """
            DELETE FROM stock_pack_operation_deleted
        """
        openupgrade.logged_query(env.cr, query)

    _logger.info(
        "Following pickings will be deleted: %(picking_names)s",
        {"picking_names": ",".join(pickings.mapped("name"))},
    )
    pickings.unlink()


@openupgrade.migrate()
def migrate(env, version):
    _migrate_pickings(env)
