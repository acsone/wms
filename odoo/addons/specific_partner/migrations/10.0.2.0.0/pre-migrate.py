# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("View")
    if not version:
        return
    empty_view = """<?xml version="1.0"?>
<data></data>
    """

    cr.execute(
        """
        update ir_ui_view set arch_db=%(empty_view)s where arch_db like %(is_veterinary)s
    """,
        {"empty_view": empty_view, "is_veterinary": """%is_veterinary%"""},
    )
