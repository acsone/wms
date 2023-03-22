# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    addons_to_uninstall = []
    for addon in addons_to_uninstall:
        _logger.info("uninstall %s", addon)
        cr.execute(
            "update ir_module_module set state = 'to remove' where name = %s",
            (addon,),
        )
