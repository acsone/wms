# -*- coding: utf-8 -*-
# © 2018 Okia SPRL <Sylvain Van Hoof>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Code ABC",
    "version": "10.0.1.0.0",
    "author": "Okia SPRL",
    "license": "AGPL-3",
    "category": "Others",
    "description": """
    Code ABC
    """,
    "depends": ["product", "purchase"],
    "data": [
        "views/code_abc.xml",
        "views/product_category.xml",
        "views/product_template.xml",
        "views/purchase_config_settings.xml",
        "security/ir.model.access.csv",
    ],
    "website": "http://www.camptocamp.com",
    "installable": True,
}
