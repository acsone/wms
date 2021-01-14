# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Sale Statistics",
    "description": """
        Add a way to export report for a specific customer""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        "stock",
        "product",
        "specific_product",
        "specific_partner",
        "stock_delivery_note",
    ],
    "data": [
        "views/res_partner.xml",
        "views/alc_stock_move_report.xml",
        "security/alc_sale_statistics_security.xml",
    ],
    "demo": [],
}
