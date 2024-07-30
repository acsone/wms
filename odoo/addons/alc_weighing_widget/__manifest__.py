# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Weighing Widget",
    "description": """
        Alcyon: Add widget to get weight from pywebdriver server with the mettler_toledo_driver""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Custom
        "alc_pywebdriver",
        # OCA
        "web_notify",
    ],
    "data": [],
    "demo": [],
    "assets": {
        "web.assets_backend": [
            "alc_weighing_widget/static/src/components/web_scale/web_scale.js",
            "alc_weighing_widget/static/src/components/web_scale/web_scale.scss",
            "alc_weighing_widget/static/src/components/web_scale/web_scale.xml",
        ]
    },
    "installable": True,
}
