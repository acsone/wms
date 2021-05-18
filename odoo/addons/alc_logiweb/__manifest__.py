# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Logiweb",
    "description": """
        Alcyon: Logiweb connector""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "alc_b2c_connector",
        "alc_b2c_connector_pricelist_discount",
        "alc_delivery_carrier_gls",
    ],
    "data": [
        "data/ir_filters.xml",
        "data/auth_api_key.xml",
        "data/alc_b2c_backend.xml",
        "data/res_partner.xml",
    ],
    "demo": [],
    "post_init_hook": "post_init_hook",
}
