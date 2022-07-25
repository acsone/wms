# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from psycopg2.extensions import AsIs

_logger = logging.getLogger(__name__)


def column_exists(cr, tablename, columnname):
    """ Return whether the given column exists. """
    query = """ SELECT 1 FROM information_schema.columns
                WHERE table_name=%s AND column_name=%s """
    cr.execute(query, (tablename, columnname))
    return cr.rowcount


def migrate_many2one_to_many2many(
    cr, tablename, column_name, relation_name, column_1, column_2
):
    if column_exists(cr, tablename, column_name):
        _logger.info(
            "Migrating %s many2one to many2many relation %s", column_name, relation_name
        )

        query_create = """
    CREATE TABLE IF NOT EXISTS %s (
       %s INTEGER NOT NULL,
       %s INTEGER NOT NULL
    );
            """
        query_create_args = (AsIs(relation_name), AsIs(column_1), AsIs(column_2))
        cr.execute(query_create, query_create_args)

        query_values = """
            SELECT id, %s
            FROM %s
            WHERE %s IS NOT NULL
        """
        query_values_args = (AsIs(column_name), AsIs(tablename), AsIs(column_name))
        cr.execute(query_values, query_values_args)
        values = cr.fetchall()

        if values:
            query_load = """INSERT INTO %s(%s, %s) VALUES %s;"""
            query_load_args = query_create_args + (AsIs(str(values)[1:-1]),)
            cr.execute(query_load, query_load_args)


def migrate(cr, version):
    if not version:
        return
    migrate_many2one_to_many2many(
        cr,
        "res_partner",
        "discount_pricelist_id",
        "partner_discount_pricelist_rel",
        "partner_id",
        "pricelist_id",
    )
    migrate_many2one_to_many2many(
        cr,
        "sale_order",
        "discount_pricelist_id",
        "order_discount_pricelist_rel",
        "order_id",
        "pricelist_id",
    )
