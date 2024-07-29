# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Storage Temperature",
    "description": """
        This is addon adds product storage temperature""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # fmt: off
        # Others
        "product",
        # fmt: on
    ],
    "data": [
        "data/product_storage_temperature.xml",
        "security/product_storage_temperature.xml",
        "views/product_template.xml",
        "views/product_product.xml",
    ],
    "pre_init_hook": "pre_init_hook",
}
