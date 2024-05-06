# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _uninstall_account_invoice_sent(env):
    """Uninstall account_invoice_sent -> account_invoice_transmit."""
    query = """
        UPDATE ir_module_module
            SET state = 'to remove'
            WHERE name = 'account_invoice_sent'
    """
    env.cr.execute(query)


@openupgrade.migrate()
def migrate(env, version):
    _uninstall_account_invoice_sent(env)
