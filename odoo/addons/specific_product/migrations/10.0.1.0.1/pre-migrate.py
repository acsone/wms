# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Reset views")

    cr.execute(
        """delete  from ir_ui_view where arch_db like '%%count_moves_to_do%%';
    """
    )
