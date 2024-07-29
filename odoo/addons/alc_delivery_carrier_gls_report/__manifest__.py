# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Gls Report Logiweb Customizations",
    "description": """Alcyon: Gls Report Customizations for Logiweb""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # Custom
        "alc_delivery_carrier_gls_b2c",
        # fmt: on
    ],
    "data": ["reports/report_delivery_report_gls.xml"],
    "demo": [],
    "installable": True,
}
