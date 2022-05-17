# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def column_exists(cr, tablename, columnname):
    """ Return whether the given column exists. """
    query = """ SELECT 1 FROM information_schema.columns
                WHERE table_name=%s AND column_name=%s """
    cr.execute(query, (tablename, columnname))
    return cr.rowcount


def post_init_hook(cr, registry):
    if not column_exists(cr, "shopinvader_variant", "to_update"):
        return
    _logger.info("Mark product with multi images to re export")
    cr.execute(
        """
        UPDATE
            shopinvader_variant
        SET
            to_update = 'true'
        WHERE
            record_id IN (
                SELECT
                    id
                FROM
                    product_product
                WHERE
                    product_tmpl_id IN (
                        SELECT
                            DISTINCT product_tmpl_id
                        FROM
                            product_image_relation
                        GROUP BY
                            product_tmpl_id
                        HAVING COUNT(id) > 1
                    )
            );
    """
    )
    _logger.info("%s variants to re export", cr.rowcount)
