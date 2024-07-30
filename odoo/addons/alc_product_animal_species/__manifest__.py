# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Product Animal Species",
    "description": """Product Animal Species""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # OCA
        "product_attribute_set",
    ],
    "application": False,
    "data": [
        "security/ir.model.access.csv",
        "data/animal_species.xml",
    ],
    "pre_init_hook": "pre_init_hook",
}
