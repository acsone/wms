# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alcyon eShop Categories",
    "description": """Alcyon eShop Categories integration with Shopinvader""",
    "version": "16.0.1.0.0",
    "author": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    "license": "AGPL-3",
    "category": "alc",
    "depends": [
        # Custom
        "alc_product_shop_category",
        # OCA
        "shopinvader_multi_category",
        "shopinvader_search_engine",
    ],
    "data": ["views/product_category.xml"],
    "development_status": "Alpha",
}
