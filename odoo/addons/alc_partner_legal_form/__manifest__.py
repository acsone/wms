# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Partner Legal Form",
    "description": """
        Specify the legal form of a company""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Others
        "sale",
    ],
    "data": [
        "security/alc_partner_legal_form.xml",
        "views/alc_partner_legal_form.xml",
        "views/res_partner.xml",
    ],
}
