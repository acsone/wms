# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Eshop Sale Cart Confirm",
    "description": """
        Alcyon: Manage sale_cart confirmation""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "alc_eshop_sale_cart_info",
        "alc_eshop_ordering_allowed",
        "sale_confirm_background",
        "onchange_helper",
    ],
    "data": ["data/mail_template.xml"],
    "demo": [],
    'installable': False
}