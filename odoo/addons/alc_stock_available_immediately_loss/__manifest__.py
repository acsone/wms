# Copyright 2020-2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Available Immediately Lot Loss",
    "description": """
        Remove lot loss location from stock immediately_available""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Third-party
        "stock_picking_operation_loss_quantity",
        # Alcyon
        "alc_stock_available_immediately",
    ],
    "data": ["data/stock_location.xml"],
    "installable": True,
}
