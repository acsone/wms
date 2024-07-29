# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Index Lowercase Name",
    "description": """
        Make sure Search Engine index names are lowercase.
        This if for compatibility with previous versions
        of the connector_search_engine module.""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "application": False,
    "depends": [
        # fmt: off
        # OCA
        "connector_search_engine",
        # fmt: on
    ],
}
