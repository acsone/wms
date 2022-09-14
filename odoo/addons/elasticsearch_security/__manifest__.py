# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "ElasticSearch Security",
    "description": """Allows to configure ElasticSearch Security (ES Enterprise feature)""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": ["connector_elasticsearch"],
    "application": False,
    "data": [
        "security/ir.model.access.csv",
        "views/res_partner.xml",
        "views/se_backend_elasticsearch.xml",
    ],
    "demo": [],
    'installable': False
}