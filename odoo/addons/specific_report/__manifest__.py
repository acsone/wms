# -*- coding: utf-8 -*-
# Copyright 2016-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Specific report for Alcyon",
    "version": "10.0.1.0.0",
    "author": "Camptocamp",
    "license": "AGPL-3",
    "category": "Sales",
    "depends": [
        "stock",
        "specific_base",
        "report",
        "specific_account",
        "account",
        "sale",
        "delivery_rounds",
        "cash_on_delivery",
        "specific_purchase",
        "l10n_be_invoice_bba",
        "l10n_be_intrastat",
        "specific_data",
        "queue_job",
        "account_invoice_sent",
        "external_fax",
        "stock_delivery_note",
        "sale_consignment",
        "account_payment_partner",
    ],
    "website": "http://www.camptocamp.com",
    "data": [
        # Views
        "wizard/modify_serial_number.xml",
        "views/base_contact.xml",
        "views/report_template.xml",
        "views/report_deliveryslip.xml",
        "views/report_invoice.xml",
        "views/report_delivery_round.xml",
        "views/report_purchase_order.xml",
        "views/report_passport.xml",
        "views/round_instance.xml",
        "views/report_saleorder_document.xml",
        "views/report_stockpicking_operations.xml",
        "views/res_partner.xml",
        # Data
        "views/stock_move.xml",
        "data/paperformat.xml",
        "data/report_filename.xml",
        "data/mail_template.xml",
    ],
    "installable": True,
}
