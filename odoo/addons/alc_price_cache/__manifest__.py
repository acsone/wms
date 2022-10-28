# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "Alcyon Price Cache",
    "description": """Alcyon Price Cache""",
    "version": "10.0.1.0.2",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "price_compute",
        "base_partition",
        "mixin_past",
        "queue_job",
        "pricelist_role_name",
        "alc_pricelist_discount",
        "alc_pricing_constraints",  # many assumptions rely on it
    ],
    "application": False,
    "data": [],
    "demo": [],
    "installable": True,
    "post_init_hook": "post_init_hook",
}
