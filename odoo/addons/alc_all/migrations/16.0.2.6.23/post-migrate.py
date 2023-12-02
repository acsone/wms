# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Migration script (init hook) is wrong on product_packaging_level module
    if openupgrade.column_exists(env.cr, "product_packaging", "packaging_type_id"):
        query = """
            UPDATE product_packaging
                SET packaging_level_id = packaging_type_id
                WHERE packaging_type_id IS NOT NULL AND packaging_type_id <> 1;
        """
        openupgrade.logged_query(env.cr, query)
        query = """
            ALTER TABLE product_packaging
                DROP COLUMN packaging_type_id
        """
        openupgrade.logged_query(env.cr, query)
