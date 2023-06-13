# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _update_package_type(env):
    """
    Keep only package types 'GLS: Parcel' on stock quant packages.

    that are in 'Customer' location.
    """

    query = """
        UPDATE stock_quant_package sqp
            SET package_type_id = NULL
            WHERE EXISTS (SELECT 1 FROM stock_location WHERE id = sqp.location_id AND usage = 'customer')
            AND package_type_id IS NOT NULL AND package_type_id NOT IN (19164, 22117);
    """
    openupgrade.logged_query(env.cr, query)


@openupgrade.migrate()
def migrate(env, version):
    _update_package_type(env)
