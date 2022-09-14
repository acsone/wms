# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc GLS: send package at 'put in pack' step",
    "description": """Alcyon: GLS shipping customizations""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "alc_weighing_widget",
        "delivery_carrier_label_gls",
        "web_domain_field",  # v10 (to remove at migration)
        "stock_picking_subcode",  # subcode in button visibility domain
        "stock_picking_assignment",  # operator in button visibility domain
    ],
    "data": ["wizards/delivery_package_gls_wizard.xml", "views/stock_picking.xml"],
    "demo": [],
    'installable': False
}