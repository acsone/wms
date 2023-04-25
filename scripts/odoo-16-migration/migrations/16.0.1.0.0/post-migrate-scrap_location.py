# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _migrate_scrap_location(env):
    # Use the existing data to company default scrap location
    location_id = env.ref("__setup__.stock_location_scrap_quality").id
    query = """
        UPDATE res_company
            SET scrap_default_location_id = %(id)s
    """
    openupgrade.logged_query(env.cr, query, {"id": location_id})


@openupgrade.migrate()
def migrate(env, version):
    _migrate_scrap_location(env)
