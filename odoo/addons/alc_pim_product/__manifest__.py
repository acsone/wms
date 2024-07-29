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
        # fmt: off
        # Custom
        "alc_pim_attribute_group",
        # OCA
        "product_attribute_set",
        # fmt: on
    ],
    "application": False,
    "data": ["data/attribute_attribute.xml", "views/product_template.xml"],
    "demo": [],
}
