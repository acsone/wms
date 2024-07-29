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
        # fmt: off
        # Custom
        "alc_product_food",
        "alc_product_pharmacy",
        # OCA
        "base_sparse_field_list_support",
        # fmt: on
    ],
    "application": False,
    "data": ["views/res_partner.xml"],
    "demo": [],
    "installable": True,
}
