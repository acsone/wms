# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def _migrate_method(env):
    if not openupgrade.column_exists(
        env.cr, "res_partner", "invoice_sending_method_old"
    ):
        return

    query = """
        INSERT INTO ir_property (name, type, res_id, value_reference, fields_id, create_date, create_uid)
        SELECT 'customer_invoice_transmit_method_id', 'many2one', 'res.partner' || ',' || rp.id, 'transmit.method' || ',' || tm.id, imf.id, NOW(), 1
            FROM res_partner rp
                INNER JOIN transmit_method tm ON rp.invoice_sending_method_old = tm.code,
            ir_model_fields imf
        WHERE NOT EXISTS (SELECT 1 FROM ir_property WHERE res_id = 'res.partner' || ',' || rp.id and value_reference = 'transmit.method' || ',' || tm.id)
        AND imf.model = 'res.partner' AND imf.name = 'customer_invoice_transmit_method_id'
    """
    openupgrade.logged_query(env.cr, query)

    query = """
        UPDATE account_move
            SET transmit_method_id =
                (SELECT split_part(value_reference, ',', 2)::integer FROM ir_property, ir_model_fields imf WHERE split_part(res_id, ',', 1) = 'res.partner' AND split_part(res_id, ',', 2)::integer = account_move.partner_id
                    AND imf.model = 'res.partner' AND imf.name = 'customer_invoice_transmit_method_id' AND fields_id = imf.id
                )

    """
    openupgrade.logged_query(env.cr, query)

    query = """
        ALTER TABLE res_partner DROP COLUMN invoice_sending_method_old
    """
    openupgrade.logged_query(env.cr, query)


@openupgrade.migrate()
def migrate(env, version):
    _migrate_method(env)
