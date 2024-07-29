# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Pharmacy Product fields",
    "description": """Alcyon Pharmacy Product fields""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # Custom
        "alc_product_category_data",
        "alc_product_category_property",
        # OCA
        "product_manufacturer",
        # fmt: on
    ],
    "application": False,
    "data": ["views/product_template.xml", "views/product_product.xml"],
    "demo": [],
    "installable": True,
}
