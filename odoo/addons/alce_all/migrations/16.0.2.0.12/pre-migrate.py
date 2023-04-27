# Copyright 2023 ACSONE SA/NV

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Marking enterprise modules to remove")
    to_remove = [
        "stock_sms",
        "quality_control",
    ]
    cr.execute(
        "update ir_module_module set state = 'to remove' where name in %s",
        (tuple(to_remove),),
    )
    _logger.info("Modules %s marked to remove", ", ".join(to_remove))
