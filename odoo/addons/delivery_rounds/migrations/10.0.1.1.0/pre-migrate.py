# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return

    _logger.info("Ensure weight is put on all templates")

    cr.execute(
        "Update product_template pt set weight = pp.weight "
        "from product_product pp where pp.weight <> 0 and "
        "pt.weight = 0 and pt.id = pp.product_tmpl_id"
    )
    return
