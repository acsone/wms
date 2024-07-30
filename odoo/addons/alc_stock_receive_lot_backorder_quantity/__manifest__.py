# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Receive Lot Backorder Quantity",
    "description": """
        Allows to add the information about bakcorder quantity on receive lot wizard""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Custom
        "alc_stock_receive_lot",
        # OCA
        "stock_available_immediately",
    ],
    "data": ["wizards/stock_receive_lot.xml"],
}
