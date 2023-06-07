# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _initialize_dates(env):
    query = """
        UPDATE product_template pt
            SET pt.expiration_time = pc.expiration_time
            FROM product_category pc
            WHERE pc.id = pt.categ_id
            AND pt.expiration_time IS NOT NULL AND pt.expiration_time <> 0
    """
    openupgrade.logged_query(env.cr, query)

    query = """
        UPDATE product_template pt
            SET pt.use_time = pc.use_time
            FROM product_category pc
            WHERE pc.id = pt.categ_id AND pt.use_time IS NOT NULL AND pt.use_time <> 0
    """
    openupgrade.logged_query(env.cr, query)

    query = """
        UPDATE product_template pt
            SET pt.removal_time = pc.removal_time
            FROM product_category pc
            WHERE pc.id = pt.categ_id AND pt.removal_time IS NOT NULL AND pt.removal_time <> 0
    """
    openupgrade.logged_query(env.cr, query)

    query = """
        UPDATE product_template pt
            SET pt.alert_time = pc.alert_time
            FROM product_category pc
            WHERE pc.id = pt.categ_id AND pt.alert_time IS NOT NULL AND pt.alert_time <> 0
    """
    openupgrade.logged_query(env.cr, query)

    query = """
        UPDATE product_category
            SET use_expiration_date = True
            WHERE expiration_time <> 0
    """
    openupgrade.logged_query(env.cr, query)

    query = """
        UPDATE product_template pt
            SET use_expiration_date = True
            WHERE expiration_time <> 0
    """
    openupgrade.logged_query(env.cr, query)


@openupgrade.migrate()
def migrate(env, version):
    _initialize_dates(env)
