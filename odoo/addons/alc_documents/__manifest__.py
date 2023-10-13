# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alcyon Documents",
    "description": """Alcyon Documents""",
    "version": "10.0.1.0.2",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "alc_pg_trgm",
        "queue_job",
        # removed by refactoring "specific_report"
    ],
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "views/alc_document.xml",
        "views/res_partner.xml",
    ],
    "demo": [],
    "post_init_hook": "post_init_hook",
    'installable': False
}