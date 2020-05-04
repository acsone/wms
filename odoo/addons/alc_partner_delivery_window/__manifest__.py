# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Partner Delivery Window",
    "description": """
        Alcyon: Delivery windows contrains on partner""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": ["partner_delivery", "sales_team"],
    "data": [
        "data/alc_delivery_week_day.xml",
        "security/alc_delivery_week_day.xml",
        "security/alc_delivery_window.xml",
        "views/alc_delivery_window.xml",
        "views/res_partner.xml",
    ],
    "demo": [],
}
