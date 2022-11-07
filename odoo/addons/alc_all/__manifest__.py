# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc All",
    "description": """
        Alcyon Odoo App""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": ["base", "alc_putaway_app"],
    "application": True,
    "data": [
        "security/sale_order.xml",
        "security/product_state.xml",
        "views/product_packaging.xml",
        "views/product_template.xml",
        "views/res_partner.xml",
        "data/ir_config_parameter.xml",
    ],
    "demo": [],
}
