# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "ElasticSearch Security",
    "description": """Allows to configure ElasticSearch Security (ES Enterprise feature)""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # Custom
        "alc_queue_job_background_channel",
        "alc_se_backend_notebook",
        # OCA
        "connector_elasticsearch",
        # fmt: on
    ],
    "application": False,
    "data": [
        "security/ir.model.access.csv",
        "views/res_partner.xml",
        "views/se_backend.xml",
        "data/queue_job_channel.xml",
        "data/queue_job_function.xml",
    ],
    "demo": [],
    "external_dependencies": {"python": ["opensearch-py"]},
}
