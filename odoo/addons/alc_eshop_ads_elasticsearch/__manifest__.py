# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Eshop Ads Elasticsearch",
    "description": """
        Alcyon: Manage publication of alcyon ads to ES""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "alc_eshop_ads",
        "alc_partner_type",  # visibility
        "connector_elasticsearch",
        "elasticsearch_search",
        "queue_job_cron",
    ],
    "data": [
        "views/alc_eshop_ads.xml",
        "views/se_backend_elasticsearch.xml",
        "data/ir_cron.xml",
        "data/se_index.xml",
    ],
    "demo": [],
}
