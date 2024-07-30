# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Restrict Lot Log",
    "description": """
        This addon log the traceback each time a move line is assigned to a lot
         different then it's restrict lot. To be removed after finding the process
         responsible for this bug""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # OCA
        "stock_restrict_lot",
    ],
    "data": [],
    "demo": [],
}
