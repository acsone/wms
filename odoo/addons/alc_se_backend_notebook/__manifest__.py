# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Se Backend Notebook",
    "description": """
        This addon add a notebook to se backend""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # fmt: off
        # OCA
        "connector_search_engine",
        # fmt: on
    ],
    "data": ["views/se_backend.xml"],
    "demo": [],
}
