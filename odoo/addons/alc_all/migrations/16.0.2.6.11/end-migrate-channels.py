# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _update_comptoir(env):
    # This channel should not have partners
    query = """
        DELETE FROM res_partner_stock_release_channel_rel WHERE channel_id = 170;
    """
    openupgrade.logged_query(env.cr, query)
    # This channel should not have domain (as there is the carrier)
    query = """
        UPDATE stock_release_channel
            SET rule_domain = '[]' WHERE id = 170
    """
    openupgrade.logged_query(env.cr, query)


@openupgrade.migrate()
def migrate(env, version):
    _update_comptoir(env)
