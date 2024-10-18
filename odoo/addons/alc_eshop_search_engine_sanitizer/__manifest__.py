# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Eshop Search Engine Sanitizer",
    "summary": """Alcyon: Sanitize indexes cron operations""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Third-party
        "queue_job_cron",
        "shopinvader_search_engine",
    ],
    "data": [
        "data/ir_cron.xml",
    ],
    "demo": [],
    "development_status": "Alpha",
}
