# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Catalog Webservice",
    "description": """Alcyon: Catalog Webservices""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # Custom
        "alc_partner_type",
        "alc_product_flattened_data",
        # OCA
        "fastapi",
        "product_brand",
        # Others
        "sale",
        # fmt: on
    ],
    "demo": [],
    "installable": True,
}
