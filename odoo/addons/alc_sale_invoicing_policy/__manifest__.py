# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Sale Invoicing policy",
    "description": """
        Alcyon: Sale Invoicing policy
        -----------------------------

        Invoices sale order based on payment_mode, invoice_frequency
        and invoice_grouping.
        The invoice frequency and grouping can be specified on the payment mode.
        If a frequency and/or a grouping are defined on the payment mode,
        these values overrides the one defined on the partner.
        The frequency and/or grouping defined on the partner applies to all the
        payment mode without these informations and to sale orders created without
        payment mode
    """,
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "alc_sale_invoicing_on_transfer",
        "account",
        "account_payment_mode",
        "account_payment_sale",
        "queue_job",
    ],
    "data": ["data/ir_cron.xml", "views/sale_order.xml", "views/res_partner.xml"],
    "demo": [],
    "external_dependencies": {"python": ["openupgradelib"]},
    "pre_init_hook": "pre_init_hook",
}
