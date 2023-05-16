# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _initialize_release_channel(cr):
    query = """
        UPDATE stock_release_channel
            SET propagate_to_pickings_chain = True
    """
    openupgrade.logged_query(cr, query)


def post_init_hook(cr, registry):
    _initialize_release_channel(cr)
