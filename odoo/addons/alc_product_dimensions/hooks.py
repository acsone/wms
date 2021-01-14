# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

_logger = logging.getLogger(__name__)


def _update_product_product(cr, registry):
    _logger.info("Update product product from product_template with existing values")
    cr.execute(
        """
        UPDATE
            product_product pp
            SET length = pt.length,
                width = pt.width,
                height = pt.depth,
                volume = pt.volume
        FROM
            product_template pt
        WHERE pt.id = pp.product_tmpl_id

    """
    )


def _update_product_uom(cr, registry):
    _logger.info("Use original value for cm unit")
    cr.execute(
        """
        UPDATE
            product_uom pu
            SET active = true
        WHERE pu.id = 10

    """
    )

    cr.execute(
        """
        UPDATE
            product_uom pu
            SET active = false
        WHERE pu.id = 29

    """
    )


def _delete_useless_columns_product_template(cr, registry):
    _logger.info("Use original value for cm unit")
    cr.execute(
        """
        ALTER TABLE
            product_template
            DROP COLUMN length,
            DROP COLUMN width,
            DROP COLUMN depth,
            DROP COLUMN volume

    """
    )


def post_init_hook(cr, registry):
    _update_product_product(cr, registry)
    _update_product_uom(cr, registry)
    _delete_useless_columns_product_template(cr, registry)
