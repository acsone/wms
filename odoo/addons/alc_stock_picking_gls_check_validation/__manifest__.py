# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Picking Gls Check Validation",
    "description": """
        Check that everything (medicine and food) is done before validating a picking
        out for gls deliveries""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        # Custom
        "alc_delivery_carrier_gls",
        "alc_gls_putinpack",
    ],
    "data": ["views/stock_picking.xml"],
    "demo": [],
    "installable": True,
}
