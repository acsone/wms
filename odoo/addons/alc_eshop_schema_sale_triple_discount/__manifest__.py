# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Eshop Sale Triple Discount",
    "description": """
        Alcyon: Adapte discount info to sale_triple_discount""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # Custom
        "alc_eshop_schema_sale_discount",
        # OCA
        "sale_triple_discount",
        # fmt: on
    ],
    "data": [],
    "demo": [],
    "installable": True,
    "development_status": "Alpha",
}
