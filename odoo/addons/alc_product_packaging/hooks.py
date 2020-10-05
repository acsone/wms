# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openupgradelib import openupgrade
from psycopg2.extensions import AsIs

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def _column_exists(cr, col_name):
    cr.execute(
        """
        SELECT
            column_name
        FROM
            information_schema.columns
        WHERE
            table_name = 'product_template' and column_name = %s;
    """,
        (col_name,),
    )
    return cr.fetchall()


def _create_product_packagings(cr):
    _logger.info("Create packagings")
    env = api.Environment(cr, SUPERUSER_ID, {})
    sequence = 4
    for packaging_type, field_name in [
        (
            env.ref("alc_product_packaging.product_packaging_type_palette"),
            "unit_in_pallet",
        ),
        (env.ref("alc_product_packaging.product_packaging_type_box"), "unit_in_box"),
        (
            env.ref("alc_product_packaging.product_packaging_type_shrink_wrap"),
            "unit_in_shrink_wrap",
        ),
    ]:
        if not _column_exists(cr, field_name):
            continue
        sql = """
            INSERT INTO product_packaging
            (create_uid, create_date, sequence, qty, product_tmpl_id, packaging_type_id, name)
            SELECT
                1,
                CURRENT_TIMESTAMP,
                %s,
                %s,
                id,
                %s,
                %s
            from product_template where %s > 0
        """
        cr.execute(
            sql,
            (
                sequence,
                AsIs(field_name),
                packaging_type.id,
                packaging_type.name,
                AsIs(field_name),
            ),
        )
        sequence -= 1


def pre_init_hook(cr):
    openupgrade.update_module_moved_fields(
        cr,
        "product_template",
        ["unit_in_shrink_wrap", "unit_in_box", "unit_in_palette"],
        "stock_unit",
        "alc_product_packaging",
    )


def post_init_hook(cr, registry):
    _create_product_packagings(cr)
