# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Fix lat long")
    if not version:
        return

    cr.execute(
        """
        alter table res_partner drop constraint res_partner_ref_digit_only
    """
    )
