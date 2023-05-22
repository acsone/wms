# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade
from psycopg2.extensions import AsIs


@openupgrade.migrate()
def migrate(env, version):
    index_name = "sale_order_line_remains_to_deliver_index"
    query = """DROP INDEX IF EXISTS %s;"""
    env.cr.execute(query, (AsIs(index_name),))
