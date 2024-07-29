# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Partner eShop Domain",
    "description": """Alcyon: Partner eShop Domain""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # Custom
        "alc_partner_type",
        # OCA
        "product_assortment",
        # fmt: on
    ],
    "data": ["data/shopinvader_assortment.xml"],
}
