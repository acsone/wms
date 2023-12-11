# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Eshop Product On Order",
    "description": """
        Aclyon EShop: Products on order management services""",
    "version": "16.0.1.0.1",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "sale",
        "alc_sale_product_qty_unavailable",
        "alc_sale_order_line_product_type",
        "alc_product_pharmacy",
        "alc_product_food",
        "alc_sale_consignment",
        "alc_sale_channel",
        "alc_cerberus_utils",
        # OCA
        "fastapi",
        "product_route_mto",
        "sale_order_line_cancel",
    ],
    "data": ["data/mail_template.xml", "security/alc_eshop_product_on_order.xml"],
    "demo": [],
    "installable": True,
}
