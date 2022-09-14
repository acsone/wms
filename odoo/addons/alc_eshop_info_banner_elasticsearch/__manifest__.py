# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Eshop Info Message Elasticsearch",
    "description": """
        Alcyon: export info banners to elasticsearch""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "alc_cerberus_utils",
        "alc_eshop_info_banner",
        "connector_elasticsearch",
        "elasticsearch_search",
        "queue_job_cron",
    ],
    "data": [
        "views/alc_eshop_info_banner.xml",
        "views/se_backend_elasticsearch.xml",
        "data/ir_cron.xml",
        "data/se_index.xml",
    ],
    "demo": [],
    'installable': False
}