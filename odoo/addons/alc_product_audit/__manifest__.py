# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Audit",
    "description": """
        Custom filter for Alcyon products""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        # Odoo Community
        "product",
        "purchase_stock",
        "stock",
        # Third-party
        "product_route_mto",
        "sale_order_line_cancel",
        "stock_location_zone",
        # Alcyon
        "alc_product_dimensions_missing",
        "alc_product_pharmacy",
        "alc_product_supplier",
        "alc_product_web_publish",
        # Alcyon/Stock Management
        "alc_stock_orderpoint_product",
    ],
    "data": ["views/product_template.xml"],
    "demo": [],
    "installable": True,
}
