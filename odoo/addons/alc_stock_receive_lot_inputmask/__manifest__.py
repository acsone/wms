# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Receive Lot Inputmask",
    "description": """
        Alcyon: Add input mask on life date field

        This addon mixes LGPL and AGPL addon to keep alc_stock_receive_lot LGPL
        and avoid licence conflict later
        """,
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": ["alc_stock_receive_lot", "LGPL" "web_widget_inputmask"],
    "data": ["views/stock_pack_operation_lot_add.xml"],
    "demo": [],
}
