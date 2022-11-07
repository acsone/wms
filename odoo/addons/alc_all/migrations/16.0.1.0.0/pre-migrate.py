# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    ADDONS_TO_UNINSTALL = ["alc_stock_picking_policy_block", "stock_reassign_auto"]
    _logger.info("uninstall %s", ",".join(ADDONS_TO_UNINSTALL))
    cr.execute(
        "update ir_module_module set state = 'to remove' where name in %s",
        (tuple(ADDONS_TO_UNINSTALL),),
    )
