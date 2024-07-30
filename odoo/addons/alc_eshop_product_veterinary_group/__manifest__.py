# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Eshop Product Veterinary Group",
    "description": """
        This addon add product veterinary group to the product schema""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Custom
        "alc_elasticsearch_security_vt_groups",
        "alc_veterinary_group",
        # OCA
        "shopinvader_product",
    ],
    "data": [],
    "demo": [],
    "development_status": "Alpha",
}
