# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Orders Webservice",
    "description": """Alcyon: Orders Webservices""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Custom
        "alc_cerberus_utils",
        "alc_sale_channel",
        "alc_sale_suite_name",
        # OCA
        "fastapi",
        "sale_cart",
        "sale_order_line_cancel",
        "shopinvader_sale_state",
    ],
    "demo": [],
    "installable": True,
    "development_status": "Alpha",
}
