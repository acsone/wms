# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Delivery Methods",
    "description": """Alcyon: Delivery methods: specify the delivery carrier available for the website""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Others
        "delivery",
    ],
    "data": [
        "views/delivery_carrier.xml",
    ],
    "installable": True,
    "post_init_hook": "post_init_hook",
}
