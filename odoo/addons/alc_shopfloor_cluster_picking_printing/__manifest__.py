# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Shopfloor Cluster Picking Printing",
    "description": """
        Alcyon: Automatic printing of product labels and packages labels into
        the cluster picking process""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "alc_package_label_printer",
        "alc_product_label_printer",
        "alc_shopfloor_packing",
        "specific_print",
    ],
    "data": ["views/shopfloor_menu.xml"],
    "demo": [],
    'installable': False
}