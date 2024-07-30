# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Discount Webservice",
    "description": """Alcyon: Discount Webservices""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Custom
        "alc_partner_pricelist",
        "alc_partner_type",
        "alc_supplier_promotion",
        # OCA
        "fastapi",
    ],
    "demo": [],
    "installable": True,
}
