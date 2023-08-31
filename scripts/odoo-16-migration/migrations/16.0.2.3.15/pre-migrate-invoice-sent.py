# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def _migrate_fields(env):
    if not openupgrade.column_exists(env.cr, "account_invoice", "sent"):
        return
    query = """
        UPDATE account_move
            SET is_move_sent = True
            WHERE EXISTS (SELECT 1 FROM account_invoice WHERE move_id = account_move.id AND sent = True)
            AND is_move_sent <> True
    """
    openupgrade.logged_query(env.cr, query)


def _migrate_method(env):
    if not openupgrade.column_exists(env.cr, "res_partner", "invoice_sending_method"):
        return
    query = """
        UPDATE res_partner
            SET invoice_sending_method =
                CASE
                    WHEN invoice_sending_method = 'letter' THEN 'post'
                    WHEN invoice_sending_method = 'email' THEN 'mail'
                END
        WHERE invoice_sending_method IS NOT NULL

    """
    openupgrade.logged_query(env.cr, query)

    # Rename column to avoid column deletion
    query = """
        ALTER TABLE res_partner
            RENAME COLUMN invoice_sending_method TO invoice_sending_method_old
    """
    openupgrade.logged_query(env.cr, query)


@openupgrade.migrate()
def migrate(env, version):
    _migrate_fields(env)
    _migrate_method(env)
