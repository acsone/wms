# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Stock Release Channel Import",
    "description": """
        This addon add a wizard for release channels import""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Third-party
        "stock_release_channel_geoengine",
        "stock_release_channel_plan",
        # Alcyon
        "alc_stock_release_channel_menu",
    ],
    "data": [
        "security/alc_import_delivery_zone_wizard.xml",
        "wizards/alc_import_delivery_zone_wizard.xml",
        "views/stock_release_channel.xml",
        "views/stock_release_channel_preparation_plan.xml",
    ],
    "demo": [],
    "external_dependencies": {"python": ["pyshp", "shapely"]},
}
