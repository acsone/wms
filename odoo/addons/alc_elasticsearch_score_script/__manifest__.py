# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Elasticsearch Score Script",
    "description": """
        Alcyon: Allows to configure a script_score in the elasticsearch backend
        """,
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # Custom
        "alc_connector_search_engine_put_script_mixin",
        "alc_se_backend_notebook",
        "alc_search_engine_backend",
        # fmt: on
    ],
    "data": [
        "views/se_backend.xml",
        "data/se_backend.xml",
    ],
    "demo": [],
}
