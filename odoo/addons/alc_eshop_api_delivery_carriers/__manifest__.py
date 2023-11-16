# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Delivery Carriers Webservice",
    "description": """Alcyon: Delivery Carriers Webservices""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "fastapi",
        "shopinvader_sale_cart",
        "delivery",
    ],
    "data": [
        "views/delivery_carrier.xml",
    ],
    "installable": True,
    "development_status": "Alpha",
    "post_init_hook": "post_init_hook",
}
