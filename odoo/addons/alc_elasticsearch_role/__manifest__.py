# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Elasticsearch Role",
    "description": """
        This addon adds elasticsearch role data""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # fmt: off
        # Custom
        "alc_search_engine_backend",
        "elasticsearch_security",
        # fmt: on
    ],
    "data": ["data/elasticsearch_role.xml"],
    "pre_init_hook": "pre_init_hook",
}
