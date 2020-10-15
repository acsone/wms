# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Delivery Rounds Geooptimize",
    "description": """
        Alcyon: Geo Optimize Delivery Rounds""",
    "version": "10.0.1.0.1",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "alc_partner_delivery_window",
        "base_geolocalize",
        "delivery_rounds",
        "queue_job",
        "stock",
    ],
    "data": [
        "views/res_partner.xml",
        "views/round_template.xml",
        "wizards/stock_config_settings.xml",
        "views/round_instance.xml",
        "data/ir_config_parameter.xml",
    ],
    "demo": [],
    "post_init_hook": "post_init_hook",
    "external_dependencies": {"python": ["requests"]},
}
