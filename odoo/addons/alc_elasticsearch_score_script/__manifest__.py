# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Elasticsearch Score Script",
    "description": """
        Alcyon: Allows to configure a script_score in the elasticsearch backend
        """,
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": ["alc_search_engine", "queue_job_cron"],
    "data": ["views/se_backend_elasticsearch.xml", "data/elasticsearch_backend.xml"],
    "demo": [],
    "installable": True,
}
