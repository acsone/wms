# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    _logger.info(
        "Enable error logging for zero or negative quantity update on stock move lines"
    )
    env["res.company"].search([]).write({"restrict_move_line_quantity": True})
