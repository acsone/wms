# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Purchase Order Cleaner",
    "description": """
        Alcyon: Removes empty lines (with qty =0) from PO on confirm""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # Others
        "purchase",
        # fmt: on
    ],
    "installable": True,
}
