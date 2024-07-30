# Copyright 2021-2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Abc Classification Storage Type",
    "description": """
        Alcyon: Auto assign classification profile based on product storage type""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # OCA
        "product_abc_classification_sale_stock",
        "product_route_mto",
        "stock_storage_type",
    ],
    "data": ["views/stock_package_type.xml", "views/abc_classification_profile.xml"],
}
