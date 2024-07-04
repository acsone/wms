# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Location Putaway Rule Out",
    "description": """
        This addon highlights the putaway rules having for a given location as destination.
        With this module, users will be able to filter locations without a putaway rule.

        """,
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": ["stock"],
    "data": [
        "views/stock_location.xml",
    ],
    "demo": [],
}
