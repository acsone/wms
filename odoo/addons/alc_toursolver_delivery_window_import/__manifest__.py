# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Toursolver Delivery Window Import",
    "description": """
        Add wizard to allows import of delivery window from csv file""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Custom
        "alc_b2c_partner",
        # OCA
        "shipment_advice_planner_toursolver",
        # Others
        "contacts",
    ],
    "data": [
        "wizards/alc_delivery_window_importer.xml",
        "security/alc_delivery_window_importer.xml",
    ],
    "demo": [],
    "external_dependencies": {"python": ["xlrd"]},
    "installable": True,
}
