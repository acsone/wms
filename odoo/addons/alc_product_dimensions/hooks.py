# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

_logger = logging.getLogger(__name__)


def column_exists(cr, tablename, columnname):
    """ Return whether the given column exists. """
    query = """ SELECT 1 FROM information_schema.columns
                WHERE table_name=%s AND column_name=%s """
    cr.execute(query, (tablename, columnname))
    return cr.rowcount


def _update_product_product(cr):
    _logger.info("Update product product from product_template with existing values")
    if column_exists(cr, "product_template", "length"):
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


def _update_product_uom(cr):
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


def _put_default_uom_id_on_products(cr):
    _logger.info("Default unit for Alcyon is cm")
    # Default unit for Alcyon is cm
    cr.execute(
        """
        UPDATE
            product_product pp
        SET dimensional_uom_id = 10

    """
    )


def _delete_useless_columns_product_template(cr):
    _logger.info("Drop useless columns on produt template")
    if column_exists(cr, "product_template", "length"):
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


def pre_init_hook(cr):
    _update_product_product(cr)
    _update_product_uom(cr)
    _put_default_uom_id_on_products(cr)
    _delete_useless_columns_product_template(cr)
