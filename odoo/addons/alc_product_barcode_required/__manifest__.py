# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Barcode Required",
    "description": """
        Check barcode required on products""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        # fmt: off
        # Custom
        "alc_product_is_new",
        # fmt: on
    ],
    "data": [
        "views/product_template.xml",
        "views/product_product.xml",
    ],
    "external_dependencies": {"python": ["openupgradelib"]},
    "installable": True,
}
