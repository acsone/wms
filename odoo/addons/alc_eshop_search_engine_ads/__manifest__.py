# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "alc eshop search engine ads",
    "description": """
        Alcyon: Manage publication of alcyon ads to ES""",
    "version": "16.0.1.0.1",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Custom
        "alc_eshop_ads",
        # OCA
        "connector_search_engine",
        "queue_job_cron",
    ],
    "data": [
        "views/alc_eshop_ads.xml",
        "views/se_backend.xml",
        "data/ir_cron.xml",
        "data/se_index.xml",
    ],
    "demo": [],
    "development_status": "Alpha",
    "pre_init_hook": "pre_init_hook",
}
