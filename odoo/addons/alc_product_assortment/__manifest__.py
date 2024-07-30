# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Assortment",
    "description": """
        Add a group to manage product assortment""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # OCA
        "product_assortment",
    ],
    "data": [
        "security/res_groups.xml",
        "views/product_assortment.xml",
    ],
    "demo": [],
}
