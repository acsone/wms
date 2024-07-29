# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Notice",
    "description": """Alcyon Product Notice""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # Custom
        "alc_queue_job_background_channel",
        # OCA
        "queue_job_cron",
        # Others
        "product",
        # fmt: on
    ],
    "data": [
        "data/ir_cron.xml",  # weekly check: create jobs
        "data/queue_job_function.xml",
        "views/product_template.xml",
    ],
    "demo": [],
}
