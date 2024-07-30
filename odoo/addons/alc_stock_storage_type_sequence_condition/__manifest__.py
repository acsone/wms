# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Storage Type Sequence Condition",
    "description": """
        Allows to define some data on condition sequences""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # OCA
        "stock_available_location_orderpoint",
        "stock_location_orderpoint",
        "stock_storage_type",
        # Others
        "product_expiry",
    ],
    "data": [
        "data/stock_storage_location_sequence_condition.xml",
    ],
    "pre_init_hook": "pre_init_hook",
}
