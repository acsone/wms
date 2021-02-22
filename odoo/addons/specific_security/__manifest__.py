# -*- coding: utf-8 -*-
# © 2018 Sylvain Van Hoof
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Specific security for Alcyon",
    "version": "10.0.1.0.0",
    "author": "Sylvain Van Hoof (Okia SPRL)",
    "license": "AGPL-3",
    "category": "Others",
    "description": """
    Specific security for Alcyon
    """,
    "depends": [
        "stock",
        "account",
        "sale",
        "mrp",
        "specific_data",
        "account_cutoff_base",
        "product_assortment",
        "base_rest",
    ],
    "data": [
        # Security
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "security/ir_rule.xml",
        # views
        "views/base_rest_view.xml",
        "views/product_assortment.xml",
    ],
    "website": "http://www.camptocamp.com",
    "installable": True,
}
