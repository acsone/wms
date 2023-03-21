# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _stock_change_product_quantity_fields(env):
    # remove location_id and corresponding FK

    # remove FK
    query = """
        ALTER TABLE stock_change_product_qty
        DROP CONSTRAINT IF EXISTS stock_change_product_qty_location_id_fkey
    """
    env.cr.execute(query)

    # remove field
    query = """
        ALTER TABLE stock_change_product_qty
        DROP COLUMN IF EXISTS location_id
    """
    env.cr.execute(query)


@openupgrade.migrate()
def migrate(env, version):
    _stock_change_product_quantity_fields(env)
