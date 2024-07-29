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
        # fmt: off
        # Custom
        "alc_cerberus_utils",
        "alc_product_food",
        "alc_product_pharmacy",
        "alc_sale_channel",
        "alc_sale_consignment",
        "alc_sale_order_line_product_type",
        "alc_sale_product_qty_unavailable",
        # OCA
        "fastapi",
        "product_route_mto",
        "sale_order_line_cancel",
        # Others
        "sale",
        # fmt: on
    ],
    "data": ["data/mail_template.xml", "security/alc_eshop_product_on_order.xml"],
    "demo": [],
    "installable": True,
}
