# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alcyon Product Additional Price",
    "description": """
    ALCYON: add 2 new price fields on product template
            sale_price_2 and indicated_price
    """,
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # Custom
        "alc_product_pricelist_data",
        # Others
        "product",
        # fmt: on
    ],
    "application": False,
    "data": ["views/product_template_views.xml"],
    "demo": [],
    "installable": True,
}
