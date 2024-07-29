# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "Elasticsearch Security Mixin",
    "description": """Link a model to an ElasticSearch role.""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # Custom
        "elasticsearch_security",
        # fmt: on
    ],
    "application": False,
    "data": ["data/queue_job_function.xml"],
    "demo": [],
    "external_dependencies": {"python": ["slugify"]},
}
