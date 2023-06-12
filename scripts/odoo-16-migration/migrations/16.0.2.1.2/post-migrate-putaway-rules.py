# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _migrate_product_bin(env):
    """Copy the former stock.product.bin to putaway rules."""

    query = """
        INSERT INTO stock_putaway_rule(product_id, location_in_id, location_out_id, sequence, company_id, active)
            SELECT psb.variant_id, psb.location_id, psb.bin_location_id, psb.sequence, 1, sl.active
            FROM product_stock_bin psb
                JOIN stock_location sl ON sl.id = psb.bin_location_id
            WHERE NOT EXISTS (
                SELECT 1 FROM stock_putaway_rule WHERE product_id = variant_id)
    """

    openupgrade.logged_query(env.cr, query)


@openupgrade.migrate()
def migrate(env, version):
    _migrate_product_bin(env)
