# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openupgradelib import openupgrade


def _pre_14_0_1_0_0(env):
    query = """
            UPDATE ir_model_data
            SET module='shopfloor_manual_product_transfer'
            WHERE module='shopfloor'
            AND name = 'scenario_manual_product_transfer';
        """
    env.cr.execute(query)


def _pre_14_0_2_3_0(env):
    queries = [
        """
            ALTER TABLE stock_move_line
            ADD COLUMN IF NOT EXISTS date_planned TIMESTAMP WITHOUT TIME ZONE
        """,
        """
            UPDATE stock_move_line
            SET date_planned=m.date
            FROM stock_move m
            WHERE move_id=m.id
            AND m.state NOT IN ('done', 'cancel');
        """,
    ]
    for query in queries:
        env.cr.execute(query)


@openupgrade.migrate()
def migrate(env, version):
    _pre_14_0_1_0_0(env)
    _pre_14_0_2_3_0(env)
