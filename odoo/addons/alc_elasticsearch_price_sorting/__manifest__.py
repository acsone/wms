# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Elasticsearch Price Sorting",
    "description": """
        Alcyon: Enrich indexed product information to allows sort on net price""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # Custom
        "alc_connector_search_engine_put_script_mixin",
        "alc_se_backend_notebook",
        "alc_search_engine_backend",
        # OCA
        "queue_job_cron",
        "shopinvader_search_engine",
        # fmt: on
    ],
    "data": [
        "views/se_backend.xml",
        "data/se_backend.xml",
        "data/ir_cron.xml",
        "data/queue_job_functions.xml",
    ],
    "development_status": "Alpha",
}
