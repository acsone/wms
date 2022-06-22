# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Registration",
    "description": """Alcyon: Registration""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "mail",
        "specific_partner",  # pharmacy field
        "alc_partner_veterinary",
        "sales_team",  # for the menu
        "contacts",  # for the window action
    ],
    "data": [
        "security/res_groups.xml",
        "security/alc_registration.xml",
        "views/alc_registration.xml",
    ],
    "demo": [],
}
