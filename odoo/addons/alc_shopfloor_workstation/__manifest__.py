# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Shopfloor Workstation",
    "description": """
        Alcyon: Shopfloor Workstation""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Custom
        "alc_product_label_printer",
        # OCA
        "shopfloor_workstation",
    ],
    "data": ["views/shopfloor_workstation.xml"],
}
