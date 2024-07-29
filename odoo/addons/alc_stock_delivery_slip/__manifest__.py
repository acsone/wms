{
    "name": "Alc Stock Delivery Slip",
    "summary": "This module generates a specific delivery slip in csv format and "
    "stores it in attachment.",
    "version": "16.0.1.0.0",
    "author": "Camptocamp, ACSONE SA/NV",
    "license": "AGPL-3",
    "category": "Stock",
    "depends": [
        # fmt: off
        # Custom
        "alc_partner_veterinary",
        "alc_product_pharmacy",
        "alc_sale_suite_name",
        # OCA
        "account_tax_one_vat",
        "account_tax_one_vat_sale",
        "stock_procurement_customer",
        # Others
        "delivery",
        "product_expiry",
        # fmt: on
    ],
    "data": [
        "views/res_partner_views.xml",
        "data/email_template.xml",
        "views/stock_picking_views.xml",
        "views/stock_move_views.xml",
    ],
    "installable": True,
    "external_dependencies": {"python": ["unicodecsv", "unidecode"]},
}
