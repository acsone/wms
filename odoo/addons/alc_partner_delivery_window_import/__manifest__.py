# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Partner Delivery Window Import",
    "description": """
        Add wizard to allows import of delivery window from csv file""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": ["alc_b2c_partner", "alc_partner_delivery_window"],
    "data": ["wizards/alc_delivery_window_importer.xml"],
    "demo": [],
    "external_dependencies": {"python": ["xlrd"]},
}
