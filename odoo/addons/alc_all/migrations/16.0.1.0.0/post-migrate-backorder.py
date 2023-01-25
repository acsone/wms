# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _res_partner_fields(env):
    query = """
        UPDATE res_partner
            SET sale_reason_backorder_strategy =
                CASE
                    WHEN is_sale_back_order_cancel THEN 'cancel'
                    ELSE 'create'
    """
    env.cr.execute(query)

    query = """
        UPDATE res_partner
            SET purchase_reason_backorder_strategy =
                CASE
                    WHEN is_purchase_back_order_accepted THEN 'create'
                    ELSE 'cancel'
    """
    env.cr.execute(query)


@openupgrade.migrate()
def migrate(env, version):
    _res_partner_fields(env)
