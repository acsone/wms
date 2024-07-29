# Copyright 2016 Camptocamp SA
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Pricelist Discount",
    "version": "16.0.1.0.0",
    "author": "Camptocamp, ACSONE SA/NV",
    "license": "AGPL-3",
    "category": "Sales Management",
    "depends": [
        # fmt: off
        # Custom
        "alc_partner_pricelist",
        "alc_product_override_price",
        "alc_product_supplierinfo_default_price",
        "alc_supplier_promotion",
        # OCA
        "account_invoice_triple_discount",
        "product_price_category",
        "sale_triple_discount",
        # Others
        "sale",
        "sale_stock",
        # fmt: on
    ],
    "website": "http://www.camptocamp.com",
    "data": [
        # Views
        "views/account_move.xml",
        "views/sale_order.xml",
        "views/product_pricelist.xml",
    ],
    "installable": True,
}
