# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Receive Lot Product Info",
    "description": """
        Alcyon: Add product information on the lot reception wizards

        The informations are provided by AGPL addons. Therefore, these should
        not be put into stock_receive_lot since it must be LGPL
        """,
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # Custom
        "alc_product_lot_info",
        "alc_stock_receive_lot",
        "alc_stock_receive_lot_backorder_quantity",
        # OCA
        "stock_lot_is_archived",
        # fmt: on
    ],
    "data": ["wizards/stock_pack_operation_lot_add.xml"],
    "demo": [],
    "installable": True,
}
