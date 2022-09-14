# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Label Printing Reception",
    "description": """
        add permission for reception user to change printer""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        "base_report_to_printer",
        "alc_product_label_printer",
        "stock_receive_lot",
        "specific_print",
    ],
    "data": [
        "security/res_groups.xml",
        "wizards/select_printing_printer.xml",
        "wizards/stock_receive.xml",
    ],
    'installable': False
}