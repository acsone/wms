# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Pricelist Discount",
    "version": "16.0.1.0.0",
    "author": "Camptocamp, ACSONE SA/NV",
    "license": "AGPL-3",
    "category": "Sales Management",
    "depends": [
        "account_invoice_triple_discount",
        "product_price_category",
        "sale",
        "sale_stock",
        "sale_triple_discount",
        "alc_product_override_price",
    ],
    "website": "http://www.camptocamp.com",
    "data": [
        # Report
        "report/sale_order.xml",
        # Views
        "views/account_move.xml",
        "views/product_supplierinfo.xml",
        "views/res_partner.xml",
        "views/sale_order.xml",
    ],
    "installable": True,
}
