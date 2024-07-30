# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Dimensions",
    "description": """
        compute product product diemnsions based on product template dimensions""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        # OCA
        "product_dimension",
        # Others
        "product",
    ],
    "data": ["views/product_template.xml"],
    "installable": True,
}
