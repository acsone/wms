# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Receive Display Stock Storage Type",
    "description": """
        Display the stock storage type in the reception wizard""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        # Custom
        "alc_stock_receive_lot",
        # OCA
        "stock_storage_type",
    ],
    "data": ["wizards/stock_pack_operation_lot_add.xml"],
    "installable": True,
}
