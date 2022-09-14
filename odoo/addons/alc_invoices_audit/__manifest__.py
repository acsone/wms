# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Invoices Audit",
    "description": """
        Add custom filters for invoicing""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": ["alc_sale_invoicing_policy", "specific_partner"],
    "data": ["views/account_invoice.xml"],
    "demo": [],
    'installable': False
}