# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Eshop Classified Advertising Shopinvader Services",
    "description": """Alcyon Eshop Classified Advertising Shopinvader Services""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "fastapi",
        "alc_eshop_classifieds",
        "alc_cerberus_utils",
        # "authenticated_partner_mixin",
        # "base_jsonify", renamed to jsonifier
        # "jsonifier",
    ],
    "data": [],
    "demo": [],
    "installable": True,
}
