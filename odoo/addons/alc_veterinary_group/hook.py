# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade
from psycopg2.extensions import AsIs

_logger = logging.getLogger(__name__)


def column_exists(cr, tablename, columnname):
    query = """ SELECT 1 FROM information_schema.columns
                WHERE table_name=%s AND column_name=%s """
    cr.execute(query, (tablename, columnname))
    return cr.rowcount


def table_exists(cr, tablename):
    query = """ SELECT 1 FROM pg_tables WHERE tablename=%s """
    cr.execute(query, (tablename,))
    return cr.rowcount


def pre_init_hook(cr):
    openupgrade.update_module_moved_fields(
        cr,
        "res.partner",
        ["veterinary_group_ids"],
        "alc_partner_veterinary",
        "alc_veterinary_group",
    )
    table_name = "res_partner_veterinary_group_rel"
    if column_exists(cr, "res_partner", "veterinary_group_id") and not table_exists(
        cr, table_name
    ):
        _logger.info("Migrate veterinary groups")

        column_1 = "res_partner_id"
        column_2 = "veterinary_group_id"
        query_create = """
CREATE TABLE IF NOT EXISTS %s (
   %s INTEGER NOT NULL,
   %s INTEGER NOT NULL
);
        """
        query_args = (AsIs(table_name), AsIs(column_1), AsIs(column_2))
        cr.execute(query_create, query_args)

        query_values = """
        SELECT id, veterinary_group_id
        FROM res_partner
        WHERE veterinary_group_id IS NOT NULL
                """
        cr.execute(query_values)
        values = cr.fetchall()

        if values:
            query_load = """INSERT INTO %s(%s, %s) VALUES %s;"""
            query_load_args = query_args + (AsIs(str(values)[1:-1]),)
            cr.execute(query_load, query_load_args)
