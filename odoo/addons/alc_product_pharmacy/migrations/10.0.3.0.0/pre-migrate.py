# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("View")
    if not version:
        return

    cr.execute(
        """
       ALTER TABLE product_template
       DROP CONSTRAINT product_template_uniq_code_amm
    """
    )
