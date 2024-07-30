# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Eshop Search Engine Manual Export",
    "description": """Eshop Search Engine Manual Export""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # OCA
        "shopinvader_search_engine_update",
    ],
    "application": False,
    "data": ["data/action_product_template.xml", "data/action_product_product.xml"],
    "development_status": "Alpha",
}
