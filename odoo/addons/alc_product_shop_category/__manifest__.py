# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Web Categories",
    "description": """Alc Product Web Categories""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "product_multi_category",
        "sale",  # because of the view menu
        "alc_product_web_publish",
    ],
    "application": False,
    "data": ["data/product_category.xml", "views/product_category_views.xml"],
    "demo": [],
}
