# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Update the invoice frequency
    if openupgrade.column_exists(env.cr, "res_partner", "invoice_frequency"):
        query = """
            UPDATE res_partner
                SET invoicing_mode =
                    CASE
                        WHEN invoice_frequency = '10_days' THEN 'ten_days'
                        WHEN invoice_frequency = '14_days' THEN 'fourteen_days'
                        WHEN invoice_frequency = '1_month' THEN 'monthly'
                    END
                WHERE invoice_frequency IS NOT NULL
        """
        openupgrade.logged_query(env.cr, query)

    if openupgrade.column_exists(env.cr, "res_partner", "invoice_grouping"):
        query = """
            UPDATE res_partner
                SET invoicing_mode = 'at_shipping'
                WHERE invoice_grouping = 'by_delivery'
        """
        openupgrade.logged_query(env.cr, query)

    if openupgrade.column_exists(env.cr, "sale_order", "is_unique_invoice"):
        query = """
            UPDATE sale_order
                SET one_invoice_per_order = True
                WHERE is_unique_invoice = True
        """
        openupgrade.logged_query(env.cr, query)

    query = """
        UPDATE sale_order
            SET invoicing_mode = rp.invoicing_mode
            FROM res_partner rp WHERE rp.id = sale_order.partner_invoice_id
    """
    openupgrade.logged_query(env.cr, query)

    # Uninstall alc modules
    query = """
      UPDATE ir_module_module
        SET state='to remove'
        WHERE name IN ('alc_sale_invoicing_policy', 'alc_invoicing_on_transfer')
      """
    openupgrade.logged_query(env.cr, query)
