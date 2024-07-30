# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Registration Responsible",
    "description": """Alcyon: Eshop Registration Responsible""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Custom
        "alc_registration",
        "mixin_user_id",
    ],
    "data": ["views/alc_registration.xml", "data/mail_templates.xml"],
    "demo": [],
    "installable": True,
}
