# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade
from psycopg2.extensions import AsIs


@openupgrade.migrate()
def migrate(env, version):
    indexes = (
        "product_template_mismatch_picking_bin_index",
        "product_template_sale_not_ok_archived_bin_available_index",
    )
    query = """DROP INDEX IF EXISTS %s"""
    for index in indexes:
        env.cr.execute(query, (AsIs(index),))
