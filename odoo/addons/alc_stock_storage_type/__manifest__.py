# -*- coding: utf-8 -*-
# Copyright 2021 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Storage Type",
    "version": "10.0.1.0.0",
    "description": """Alcyon: Storage Type configuration """,
    "author": "BCIM",
    "license": "AGPL-3",
    "category": "",
    "depends": ["stock_storage_type_putaway_abc"],
    "data": [
        "data/stock_location_storage_type.xml",
        "data/stock_package_storage_type.xml",
        "data/stock_location.xml",
        "data/stock_storage_location_sequence.xml",
    ],
    "demo": [],
    "pre_init_hook": "pre_init_hook",
}
