# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Search Engine Backend",
    "description": """
        This addon adds search engine backend for alc""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Custom
        "alc_se_index_lowercase_name",
        # OCA
        "connector_elasticsearch",
    ],
    "data": ["data/se_backend.xml"],
    "pre_init_hook": "pre_init_hook",
    "demo": [],
}
