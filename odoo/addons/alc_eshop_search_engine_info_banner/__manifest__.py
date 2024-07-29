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
        # fmt: off
        # Custom
        "alc_eshop_info_banner",
        # OCA
        "connector_search_engine",
        "queue_job_cron",
        # fmt: on
    ],
    "data": [
        "views/se_backend.xml",
        "views/alc_eshop_info_banner.xml",
        "data/ir_cron.xml",
        "data/se_index.xml",
    ],
    "demo": [],
}
