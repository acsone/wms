# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Category Business Unit",
    "description": """
        Business unit on product category""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        # OCA
        "product_template_has_one_variant",
    ],
    "data": ["views/product_template.xml", "views/product_category.xml"],
    "demo": [],
    "installable": True,
}
