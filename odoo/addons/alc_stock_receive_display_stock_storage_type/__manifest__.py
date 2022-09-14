# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Receive Display Stock Storage Type",
    "description": """
        Display the stock storage type in the reception wizard""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": ["stock_receive_lot", "alc_product_storage_type_tracking"],
    "data": ["wizards/stock_pack_operation_lot_add.xml"],
    'installable': False
}