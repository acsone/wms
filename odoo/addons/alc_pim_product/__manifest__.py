# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc PIM Product fields",
    "description": """Alcyon PIM Product fields""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Third-party
        "product_attribute_set",
        # Alcyon
        "alc_pim_attribute_group",
    ],
    "application": False,
    "data": ["data/attribute_attribute.xml", "views/product_template.xml"],
    "demo": [],
}
