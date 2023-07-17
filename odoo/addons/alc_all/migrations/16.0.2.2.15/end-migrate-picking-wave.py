# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):

    _logger.info("Migrate draft picking waves that have no pickings to cancel")
    batches = env["stock.picking.batch"].search(
        [("state", "=", "draft"), ("picking_ids", "=", False)]
    )

    batches.write({"state": "cancel"})
