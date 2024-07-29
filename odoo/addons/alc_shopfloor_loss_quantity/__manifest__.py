# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Shopfloor Loss Quantity",
    "description": """
        This addon replace the stock issue inventory by loss quantity move in shopfloor""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # fmt: off
        # OCA
        "stock_picking_operation_loss_quantity",
        # fmt: on
    ],
    "data": [],
    "demo": [],
}
