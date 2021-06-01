# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):

    _logger.info("uninstall code_abc")
    cr.execute(
        "update ir_module_module set state = 'to remove' where name ='alc_stock_location_barcode_required'"
    )
    # initialize location
    cr.execute(
        """ WITH duplicate_location AS (
                SELECT
                    name
                FROM
                    stock_location
                GROUP BY
                    name
                HAVING count(name) > 1
            )
            UPDATE
                stock_location sl
            SET
                barcode = regexp_replace(name, '[^a-zA-Z0-9,*]+', '', 'g')
            WHERE
                barcode is null
                and not exists ( select 1 from duplicate_location where name = sl.name)
        """
    )
