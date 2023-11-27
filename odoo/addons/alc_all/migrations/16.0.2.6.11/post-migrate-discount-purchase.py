# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _move_discount_purchase_data(env):
    # Move discount_purchase data to discount field in product_supplierinfo table

    if openupgrade.column_exists(env.cr, "product_supplierinfo", "discount_purchase"):
        query = """
            UPDATE product_supplierinfo
                SET discount = discount_purchase
                WHERE discount IS NULL OR discount = 0
        """
        openupgrade.logged_query(env.cr, query)

        # Drop column - no more ir_model_fields data
        query = """
            ALTER TABLE product_supplierinfo
                DROP COLUMN discount_purchase
        """
        openupgrade.logged_query(env.cr, query)


@openupgrade.migrate()
def migrate(env, version):
    _move_discount_purchase_data(env)
