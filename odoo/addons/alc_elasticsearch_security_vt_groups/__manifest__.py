# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "Alcyon Elasticsearch Security: VT Groups",
    "description": """Compute Alcyon-specific Veterinary Groups ElasticSearch roles.""",
    "version": "16.0.2.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # Custom
        "alc_elasticsearch_security",
        "alc_veterinary_group",
        # fmt: on
    ],
    "application": False,
    "data": [],
    "demo": [],
    "post_init_hook": "post_init_hook",
    "external_dependencies": {"python": ["slugify"]},
}
