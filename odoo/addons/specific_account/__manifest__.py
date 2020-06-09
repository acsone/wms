# -*- coding: utf-8 -*-
# Copyright 2016-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Specific account for Alcyon",
    "version": "10.0.2.0.0",
    "author": "Camptocamp",
    "license": "AGPL-3",
    "category": "Sales",
    "depends": [
        "account",
        "account_cancel",
        "account_cutoff_base",
        "account_invoice_check_total",
        "account_invoice_sent",
        "analytic",
        "l10n_be_antibiotic_tax",
        "l10n_be_apb_tax",
        "l10n_be_invoice_bba",
        "sale",
        "pricelist_discount",
        "product_analytic",
        "purchase",
        "report_intrastat",
        "specific_base",
        "specific_purchase",
        "specific_shipping_costs",
        # OCA/web
        "web_readonly_bypass",
    ],
    "website": "http://www.camptocamp.com",
    "data": [
        # Data
        "data/account_tax_group.xml",
        # Views
        "views/assets.xml",
        "views/account_analytic_tag.xml",
        "views/account_cutoff.xml",
        "views/account_invoice_report.xml",
        "views/account_invoice_view.xml",
        "views/account_move_line.xml",
        "views/menu.xml",
        "views/res_config.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "external_dependencies": {"python": ["openupgradelib"]},
}
