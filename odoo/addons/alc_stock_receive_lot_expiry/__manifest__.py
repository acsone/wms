# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Receive Lot Expiry",
    "description": """
        Alcyon: Manage expiry date on dedicated reception wizard
        (stock.pack.operation.lot.add)
        """,
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Custom
        "alc_stock_receive_lot",
        # Others
        "product_expiry",
    ],
    "data": [
        "wizards/stock_pack_operation_lot_add.xml",
    ],
    "demo": [],
    "installable": True,
}
