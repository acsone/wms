# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    # initialize location
    cr.execute(
        """
            UPDATE
                stock_location sl
            SET
                barcode = concat('L#', barcode)
            WHERE
                barcode not like ('L#%')
        """
    )
