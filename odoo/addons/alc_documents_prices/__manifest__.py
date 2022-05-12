# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alcyon Documents Prices",
    "description": """Alcyon Documents Prices""",
    "version": "10.0.1.0.2",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "alc_documents",
        "alc_price_cache",
        "product_multi_category",
        "alc_supplier_promotion",
        "product_discount_specials",
        "account_tax_one_vat",
    ],
    "data": [],
    "demo": [],
    "external_dependencies": {"python": ["unicodecsv"]},
    "post_init_hook": "post_init_hook",
}
