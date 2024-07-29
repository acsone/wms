# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Product Discount Special",
    "description": """Product Discount Special""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # Custom
        "mixin_past",
        # Others
        "sale",
        # fmt: on
    ],  # security_group above product
    "application": False,
    "data": [
        "security/product_discount_special.xml",
        "views/product_discount_special.xml",
        "views/product_template.xml",
    ],
    "demo": [],
}
