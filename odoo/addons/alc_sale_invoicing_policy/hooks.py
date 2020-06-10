# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def pre_init_hook(cr):
    """Loaded before installing the module.
    :param odoo.sql_db.Cursor cr:
        Database cursor.

    """
    # Moved fields from specific_account
    openupgrade.update_module_moved_fields(
        cr,
        "res.partner",
        ["invoice_frequency", "invoice_grouping"],
        "specific_account",
        "alc_sale_invoicing_policy",
    )

    openupgrade.update_module_moved_fields(
        cr,
        "sale.order",
        ["is_unique_invoice"],
        "specific_account",
        "alc_sale_invoicing_policy",
    )

    # Moved xml_id from specific_account
    openupgrade.rename_xmlids(
        cr,
        [
            (
                "specific_account.ir_cron_invoice_10",
                "alc_sale_invoicing_policy.ir_cron_invoice_10",
            ),
            (
                "specific_account.ir_cron_invoice_20",
                "alc_sale_invoicing_policy.ir_cron_invoice_20",
            ),
            (
                "specific_account.ir_cron_invoice_31",
                "alc_sale_invoicing_policy.ir_cron_invoice_31",
            ),
        ],
    )
