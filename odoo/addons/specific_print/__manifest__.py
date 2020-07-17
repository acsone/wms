# -*- coding: utf-8 -*-
# © 2017 BCIM sprl, Camptocamp, Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Print",
    "version": "10.0.1.0.0",
    "category": "Stock Management",
    "author": "BCIM",
    "maintainer": "Camptocamp",
    "depends": [
        "alc_b2c_partner",
        "base_report_to_printer",  # OCA/report-print-send.git
        "specific_report",
        "specific_product",
        "stock",
        "stock_receive_lot",
    ],
    "data": [
        "views/stock_splitlot.xml",
        "views/printer.xml",
        "views/res_partner.xml",
        "wizards/stock_receive.xml",
        "wizards/print_label.xml",
        "report/stock_product_label.xml",
        "report/stock_pack_label.xml",
        "report/stock_lot_label.xml",
        "views/stock.xml",
        "views/product_template.xml",
        "views/stock_production_lot.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
    "application": False,
}
