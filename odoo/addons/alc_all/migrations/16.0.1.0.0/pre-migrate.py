# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):

    _logger.info("uninstall alc_stock_picking_policy_block")
    cr.execute(
        "update ir_module_module set state = 'to remove' where name in('alc_stock_picking_policy_block')"
    )
