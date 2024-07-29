# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Sale Cart Price Recalculation",
    "description": """
        Alcyon: Update date_order to today and recompute prices on cart""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # Custom
        "alc_queue_job_background_channel",
        # OCA
        "queue_job",
        "queue_job_cron",
        "sale_cart",
        # fmt: on
    ],
    "data": ["data/ir_cron.xml"],
    "demo": [],
    "installable": True,
}
