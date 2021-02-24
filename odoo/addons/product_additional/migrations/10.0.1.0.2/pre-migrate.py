# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Fix warehouse_id on additional moves")
    sql = """
    UPDATE
        stock_move
    SET
        warehouse_id = 1
    WHERE
        is_additional_move is True
    """
    cr.execute(sql)
