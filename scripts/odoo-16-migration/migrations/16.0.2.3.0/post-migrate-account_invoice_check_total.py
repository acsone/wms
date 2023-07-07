# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    env.cr.execute(
        """CREATE TEMP TABLE am_inv_mapping AS
        select move_id, max(invoice_id) as inv_id
        from account_move_line aml, invl_aml_mapping iam, account_invoice_line ail
        where invl_id = ail.id
        and aml_id = aml.id
        group by move_id"""
    )
    env.cr.execute("""CREATE INDEX tmp_invoice_idx ON am_inv_mapping (inv_id)""")
    env.cr.execute("""CREATE INDEX tmp_move_idx ON am_inv_mapping (move_id)""")
    env.cr.execute(
        """UPDATE account_move am
                      SET check_total = ai.check_total
                        FROM account_invoice ai
                        JOIN am_inv_mapping map on ai.id = map.inv_id
                      WHERE am.id = map.move_id"""
    )
