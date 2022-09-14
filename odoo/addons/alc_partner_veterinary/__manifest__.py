# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alcyon Veterinary Partner",
    "description": """Alcyon Veterinary Partner""",
    "version": "10.0.3.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": ["alc_partner_type"],
    "application": False,
    "data": ["views/res_partner.xml"],
    "demo": [],
    "pre_init_hook": "pre_init_hook",
    'installable': False
}