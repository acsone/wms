# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _stock_location_fields(env):
    # set usage as view where act_as_view is set
    query = """
        UPDATE stock_location
        SET usage = 'view'
        WHERE act_as_view = TRUE
    """
    env.cr.execute(query)


@openupgrade.migrate()
def migrate(env, version):
    _stock_location_fields(env)
