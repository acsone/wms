# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "Alcyon Price Cache",
    "description": """Alcyon Price Cache""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # OCA
        "base_partition",
        "queue_job",
        # ALC
        "mixin_past",
        "alc_pricelist_role_name",
        "alc_pricelist_discount",
        "alc_queue_job_background_channel",
    ],
    "application": False,
    "data": [
        "data/queue_job_channel.xml",
        "data/queue_job_function.xml",
    ],
    "demo": [],
    "post_init_hook": "post_init_hook",
}
