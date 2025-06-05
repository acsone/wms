# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Partner Release Channel",
    "summary": """Adds a filter and a group view for release channels on partners""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Odoo Community
        "base",
        # Third-party
        "stock_release_channel_geoengine",
    ],
    "data": [
        "views/res_partner.xml",
    ],
    "demo": [],
}
