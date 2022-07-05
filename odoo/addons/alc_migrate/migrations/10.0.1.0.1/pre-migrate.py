# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """When removing a field from the model, we have an issue: the ORM check if
    the field exists in the old view, which is not the case, and thus raises.
    Because this can happen before updating the correct module, it leaves two choices:
    doing the removal in two phases (remove from views, then from the model) or clean up
    the views before anything happens. This script handles the latter.
    """
    _logger.info("View")
    if not version:
        return
    empty_view = """<?xml version="1.0"?>
<data></data>
    """

    cr.execute(
        """
        update ir_ui_view set arch_db=%(empty_view)s where arch_db like %(field_marker)s
    """,
        {"empty_view": empty_view, "field_marker": """%veterinary_group_id%"""},
    )
