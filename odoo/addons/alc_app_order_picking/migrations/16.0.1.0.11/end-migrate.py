# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _uninstall_occupancy_module(env):
    query = """
        UPDATE ir_module_module
            SET state = 'to remove'
            WHERE name = 'stock_location_occupancy'
    """
    openupgrade.logged_query(env.cr, query)


@openupgrade.migrate()
def migrate(env, version):
    _uninstall_occupancy_module(env)
