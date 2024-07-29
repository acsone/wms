# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Shopfloor Cluster Picking Transfer Async",
    "description": """
        Alcyon: Aynchronous picking transfer on cluster_picking""",
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
        "shopfloor",
        # fmt: on
    ],
    "data": [
        "views/shopfloor_menu.xml",
        "data/queue_job_channel.xml",
        "data/queue_job_functions.xml",
    ],
    "demo": [],
}
