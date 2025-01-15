# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc search engine Eshop Info Message",
    "description": """
        Alcyon: export info banners to es""",
    "version": "16.0.1.0.1",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Third-party
        "connector_search_engine",
        "queue_job_cron",
        # Alcyon
        "alc_eshop_info_banner",
        "alc_eshop_search_engine_temporal_info_mixin",
    ],
    "data": [
        "views/se_backend.xml",
        "data/ir_cron.xml",
        "data/se_index.xml",
    ],
    "demo": [],
}
