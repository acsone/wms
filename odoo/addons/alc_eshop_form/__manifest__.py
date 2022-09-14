# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Eshop Form",
    "description": """
        Alcyon: Manage Forms on website""",
    "version": "10.0.1.0.3",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "authenticated_partner_mixin",
        "report",
        "sales_team",
        "web_widget_formio",
    ],
    "data": [
        "security/res_groups.xml",
        "security/alc_eshop_form.xml",
        "views/alc_eshop_form.xml",
        "data/alc_eshop_form.xml",
        "reports/report_alc_eshop_form_submission.xml",
    ],
    "post_init_hook": "post_init_hook",
    "external_dependencies": {"python": ["unicodecsv"]},
    'installable': False
}