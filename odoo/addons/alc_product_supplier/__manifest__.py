# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product supplier related fields",
    "description": """Alcyon Product Supplier fields""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # OCA
        "partner_manual_rank",
        # Others
        "purchase",
    ],
    "data": ["views/product_template_views.xml"],
    "demo": [],
    "installable": True,
}
