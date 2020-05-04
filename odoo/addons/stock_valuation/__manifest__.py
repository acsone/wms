# -*- coding: utf-8 -*-
# © 2017-2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Valuation",
    "version": "1.0",
    "category": "Stock Management",
    "author": "BCIM",
    "depends": [
        "stock_account",
        "specific_purchase",  # for product supplier
        "specific_base",
        "product_last_transaction",
    ],
    "data": [
        "wizards/stock_valuation_history_view.xml",
        "views/stock_quant_views.xml",
        "data/ir_cron.xml",
        "security/menu.xml",
    ],
    "installable": True,
    "active": False,
    "license": "AGPL-3",
    "application": False,
}
