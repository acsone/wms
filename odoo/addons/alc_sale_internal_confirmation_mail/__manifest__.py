# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Sale Confirmation Mailing",
    "description": """Send mails while confirming internal Orders.""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # Custom
        "alc_sale_channel",
        # OCA
        "queue_job",
        # fmt: on
    ],
    "data": ["wizards/res_config_settings.xml", "data/queue_job_function.xml"],
    "demo": [],
}
