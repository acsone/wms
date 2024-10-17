# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Customer Audit",
    "description": """ Custom filters on customer""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "depends": [
        # Odoo Community
        "delivery",
        # Third-party
        "stock_release_channel_geoengine",
        # Alcyon
        "alc_partner_manual_rank",
        "alc_partner_pharmacist",
        "alc_partner_type",
    ],
    "data": ["views/res_partner.xml"],
    "demo": [],
    "installable": True,
}
