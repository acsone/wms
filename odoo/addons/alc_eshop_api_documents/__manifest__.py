# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Eshop Documents",
    "description": """Alcyon: Webservices for customer documents""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Custom
        "alc_cerberus_utils",
        "alc_documents",
        "alc_sale_channel",
        # OCA
        "fastapi",
        "fs_attachment",
    ],
    "demo": [],
    "installable": True,
}
