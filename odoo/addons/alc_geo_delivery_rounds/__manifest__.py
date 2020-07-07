# -*- coding: utf-8 -*-
# Copyright 2020 Acsone SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc geoEngine",
    "version": "10.0.2.0.0",
    "description": """Alcyon: Improve journey planification for deliveries """,
    "author": "Acsone SA/NV",
    "website": "http://acsone.eu",
    "license": "AGPL-3",
    "category": "",
    "depends": [
        "alc_delivery_rounds_geooptimize",
        "base_geolocalize",
        "delivery_rounds",
        "geoengine_partner",
    ],
    "data": [
        "wizards/make_itinerary_plan_wizard.xml",
        "wizards/shape_file_import_wizard.xml",
        "views/delivery_plan.xml",
        "views/res_partner.xml",
        "views/round_template.xml",
        "security/ir.model.access.csv",
    ],
    "demo": [],
    "post_init_hook": "post_init_hook",
    "external_dependencies": {"python": ["shapely", "shapefile"]},
    "auto_install": True,
    "application": True,
}
