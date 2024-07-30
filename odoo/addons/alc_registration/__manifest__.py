# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Registration",
    "description": """Alcyon: Registration""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Custom
        "alc_partner_apb_authorization",
        "alc_partner_category",
        "alc_partner_opt_out",
        "alc_partner_suite",
        "alc_partner_veterinary",
        # OCA
        "partner_fax",
        # Others
        "contacts",
        "mail",
        "sales_team",
    ],
    "data": [
        "security/res_groups.xml",
        "security/alc_registration.xml",
        "views/alc_registration.xml",
        "views/res_partner.xml",
    ],
    "demo": [],
    "installable": True,
}
