# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Pricelist Discount",
    "version": "10.0.3.0.0",
    "author": "Camptocamp",
    "license": "AGPL-3",
    "category": "Sales Management",
    "depends": [
        "account_invoice_triple_discount",
        "price_compute",  # utilities on top of product
        "product_price_category",
        "sale",
        "sale_stock",
        "sale_triple_discount",
    ],
    "website": "http://www.camptocamp.com",
    "data": [
        # Report
        "report/sale_order.xml",
        # Views
        "views/account_invoice.xml",
        "views/product_supplierinfo.xml",
        "views/res_partner.xml",
        "views/sale_order.xml",
    ],
    "installable": False,
}
