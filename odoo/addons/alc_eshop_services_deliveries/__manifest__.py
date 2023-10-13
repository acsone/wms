# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Deliveries Webservice",
    "description": """Alcyon: Deliveries Webservices""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "authenticated_partner_mixin",
        # "base_jsonify", renamed to jsonifier
        "jsonifier",
        "stock_delivery_note",
        # removed by refactoring "specific_report",
        "account_tax_one_vat",
        "stock_groupbypartner",  # customer_id
    ],
    "demo": [],
    'installable': False
}