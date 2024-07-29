# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product State",
    "description": """
        Alcyon: Add some data on product_state""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # OCA
        "product_state",
        # fmt: on
    ],
    "data": [
        "data/product_state.xml",
        "views/product_template_views.xml",
    ],
    "demo": [],
    "installable": True,
}
