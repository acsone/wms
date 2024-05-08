# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    _logger.info(
        "Uninstall alc_stock_available_to_promise_immediately_exclude_location"
    )
    module = env["ir.module.module"].search(
        [("name", "=", "alc_stock_available_to_promise_immediately_exclude_location")]
    )
    module.write({"state": "to remove"})
