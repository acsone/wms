# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Sale App",
    "description": """
        Gather all Sale related modules for Alcyon""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "application": True,
    "depends": [
        # Odoo
        "sale",
        # OCA
        "sale_triple_discount",
        "product_price_category",
        # ALC
        "alc_product_category_data",
        "alc_product_pricelist_data",
        "alc_product_category_business_unit",
        "alc_product_category_property",
    ],
}
