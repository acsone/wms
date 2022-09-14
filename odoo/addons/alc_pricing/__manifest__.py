# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "Alcyon Pricing",
    "description": """Alcyon Pricing:
    Module grouping price functionality.
    Since triple discounts, supplier discounts and other features cannot be fully tested
    without grouping all these dependencies.
    """,
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "alc_price_cache_exclusive",
        "alc_price_triple_discount_exclusive",
        "alc_pricelist_discount",
        "alc_supplier_promotion",
        "onchange_helper",  # for the test
    ],
    "application": False,
    "data": [],
    "demo": [],
    "installable": False,
}
