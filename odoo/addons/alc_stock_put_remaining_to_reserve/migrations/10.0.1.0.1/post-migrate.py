# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Updating picking types")
    if not version:
        return

    cr.execute(
        """
        UPDATE stock_picking_type
        SET put_in_reserve_allowed=true
        WHERE name ilike '%Rangement%'
        RETURNING name
    """
    )
    names = [i[0] for i in cr.fetchall()]

    _logger.info("%d stock_picking_type updated: (%s)", len(names), ", ".join(names))
