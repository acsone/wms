# -*- coding: utf-8 -*-
# © 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Specific purchase for Alcyon",
    "version": "10.0.1.0.0",
    "author": "Camptocamp",
    "license": "AGPL-3",
    "category": "Purchases",
    "depends": [
        "pricelist_discount",
        "purchase",
        "stock",
        "calendar",
        "purchase_cancel_reason",
        "purchase_prepaid",
        "specific_product",
        "stock_unit",
        "stock_mts_mto_rule",
        "website_purchase_review",
    ],
    "website": "http://www.camptocamp.com",
    "data": [
        # Views
        "views/res_partner.xml",
        "views/product_template.xml",
        "views/purchase_order.xml",
        "views/bank_holiday.xml",
        "views/purchase_config_settings.xml",
        "views/product_state.xml",
        "views/product_supplierinfo.xml",
        "views/email_template.xml",
        "views/ir_ui_menu.xml",
        # Data
        "data/product_state.xml",
        "data/ir_config_parameter.xml",
        "data/ir_cron.xml",
        # Wizards
        "wizards/procurement_orderpoint_compute_views.xml",
        # Security
        "security/ir.model.access.csv",
        "security/ir_ui_menu.xml",
    ],
    "installable": True,
}
