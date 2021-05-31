# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def pre_init_hook(cr):
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
                barcode = regexp_replace(name, '[^a-zA-Z0-9]+', '', 'g')
            WHERE
                barcode is null
                and not exists ( select 1 from duplicate_location where name = sl.name)
        """
    )
