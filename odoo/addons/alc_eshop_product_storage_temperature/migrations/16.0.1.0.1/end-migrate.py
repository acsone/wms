# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _update_product_bindings(env):
    query = """
        UPDATE se_binding
            SET state = 'to_recompute'
            WHERE res_model = 'product.product'
            AND EXISTS (SELECT 1 FROM se_index si JOIN res_lang rl ON rl.id = si.lang_id WHERE si.id = index_id AND rl.code IN ('nl_BE', 'en_US'))
    """
    openupgrade.logged_query(env.cr, query)


@openupgrade.migrate()
def migrate(env, version):
    _update_product_bindings(env)
