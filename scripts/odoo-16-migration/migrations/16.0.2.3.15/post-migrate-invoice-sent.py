# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def _migrate_fields(env):
    if not openupgrade.column_exists(env.cr, "account_move", "sent"):
        return
    query = """
        UPDATE account_move
            SET is_move_sent = True
            WHERE sent = True
            AND is_move_sent <> True
    """
    openupgrade.logged_query(env.cr, query)


def _migrate_method(env):
    if not openupgrade.column_exists(env.cr, "account_move", "invoice_sending_method"):
        return
    fields_spec = [
        (
            "customer_invoice_transmit_method_id",
            "res.partner",
            "res_partner",
            "many2one",
            False,
            "account_invoice_transmit_method",
        ),
        (
            "transmit_method_id",
            "res.partner",
            "res_partner",
            "many2one",
            False,
            "account_invoice_transmit_method",
        ),
    ]
    openupgrade.add_fields(env, fields_spec)
    query = """
        UPDATE res_partner
            SET invoice_sending_method =
                CASE
                    WHEN invoice_sending_method = 'letter' THEN 'post'
                    WHEN invoice_sending_method = 'email' THEN 'mail'
        WHERE invoice_sending_method IS NOT NULL

    """
    openupgrade.logged_query(env.cr, query)
    query = """
        UPDATE res_partner
            SET customer_invoice_transmit_method_id = method_id
                FROM (SELECT id AS method_id, code FROM transmit_method) methods
            WHERE res_partner.invoice_sending_method = methods.code

    """
    openupgrade.logged_query(env.cr, query)

    # Update the transmit method on invoices
    query = """
        UPDATE account_move
            SET sending_method =
                CASE
                    WHEN sending_method = 'letter' THEN 'post'
                    WHEN sending_method = 'email' THEN 'mail'
        WHERE sending_method IS NOT NULL AND move_type IN ('out_invoice', 'out_refund')

    """
    openupgrade.logged_query(env.cr, query)

    query = """
        UPDATE account_move
            SET transmit_method_id = method_id
                FROM (SELECT id AS method_id, code FROM transmit_method) methods
            WHERE account_move.sending_method = methods.code

    """
    openupgrade.logged_query(env.cr, query)


@openupgrade.migrate()
def migrate(env, version):
    _migrate_fields(env)
    _migrate_method(env)
