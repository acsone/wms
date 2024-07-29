# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Packaging Dimension",
    "description": """
        Manage the displayed length, width and height unit of measure""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        # fmt: off
        # OCA
        "product_packaging_dimension",
        # Others
        "product",
        "uom",
        # fmt: on
    ],
    "data": ["views/product_packaging.xml", "views/res_config_settings.xml"],
    "installable": True,
}
