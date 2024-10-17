# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alcyon Customer Type",
    "description": """Product Category Properties""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Third-party
        "base_sparse_field_list_support",
        # Alcyon
        "alc_product_food",
        "alc_product_pharmacy",
    ],
    "application": False,
    "data": ["views/res_partner.xml"],
    "demo": [],
    "installable": True,
}
