# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Eshop Classified Advertising",
    "description": """Alcyon: Eshop Classified Advertising""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Custom
        "alc_address_data",
        "mixin_past",
        # OCA
        "fs_file",
        # Others
        "mail",
        "sale",
    ],
    "data": [
        "security/alc_classified.xml",
        "security/alc_classified_wizard_rejection.xml",
        "views/alc_classified.xml",
        "views/res_partner.xml",
        "wizards/alc_classified_wizard_rejection.xml",
    ],
    "demo": [],
    "external_dependencies": {"python": ["slugify"]},
    "installable": True,
    "development_status": "Alpha",
}
