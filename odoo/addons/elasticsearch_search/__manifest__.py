# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Elasticsearch Search",
    "description": """
        Elasticsearch: Add search method on connector elasticsearch""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": ["connector_elasticsearch"],
    "application": False,
    "data": [],
    "demo": [],
    "external_dependencies": {"python": ["elasticsearch_dsl"]},
    'installable': False
}