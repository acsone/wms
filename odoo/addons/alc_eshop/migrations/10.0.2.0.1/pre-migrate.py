# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):

    _logger.info("set backend to no update")
    cr.execute(
        "update ir_model_data set noupdate=true where name='backend' and module='alc_eshop';"
    )
